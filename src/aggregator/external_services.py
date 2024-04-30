import orjson
import requests
import structlog
from google.cloud import language_v1

from aggregator.parser import get_with_max_size
from config import get_config
from ext_article_categorization.taxonomy_mapping import get_channels_for_classification

client = language_v1.LanguageServiceClient()


config = get_config()
logger = structlog.getLogger(__name__)


def get_popularity_score(_article):
    """
    Calculate the popularity score for an article.

    Parameters:
        _article (dict): The dictionary representing the article to calculate the popularity score for.

    Returns:
        dict: The updated dictionary with the calculated popularity score.
    """
    url = config.bs_pop_endpoint + _article["url"]

    try:
        response = get_with_max_size(url)
        pop_response = orjson.loads(response)
        pop_score = pop_response.get("popularity", {}).get("popularity", {}) or 1.0
        pop_score_agg = sum(pop_score.values())

        if pop_score_agg <= config.pop_score_cutoff:
            return {**_article, "pop_score": pop_score_agg}

        pop_score_agg_lin = (config.pop_score_cutoff - 1) + (
            1 + pop_score_agg - config.pop_score_cutoff
        ) ** config.pop_score_exponent
        return {**_article, "pop_score": pop_score_agg_lin}

    except requests.RequestException as req_exc:
        logger.error(f"Request to {url} failed with error: {req_exc}")
        return {**_article, "pop_score": 1.0}
    except orjson.JSONDecodeError as json_exc:
        logger.error(f"Failed to decode JSON response for {url} with error: {json_exc}")
        return {**_article, "pop_score": 1.0}
    except Exception as e:
        logger.error(f"An unexpected error occurred for {url}: {e}")
        return {**_article, "pop_score": 1.0}


def get_predicted_channels(_article):
    """
    Retrieves the predicted channels for an article using the NU-API.

    Args:
        _article (dict): The article to retrieve the predicted channels for.

    Returns:
        dict: The input article with updated channels.

    Raises:
        Exception: If there is an error retrieving the predicted channels.
    """
    # Skip article if in default channels or if description + title is less than 20 characters
    if (
        bool(set(_article["channels"]).intersection(config.nu_default_channels))
        or len(_article.get("description") + _article.get("title")) < 20
    ):
        return _article

    try:
        response = requests.post(
            url=config.nu_api_url,
            json=[_article],
            headers={"Authorization": f"Bearer {config.nu_api_token}"},
            timeout=config.request_timeout,
        )
        response.raise_for_status()

        api_response = response.json()
        pred_channels = api_response.get("results")[0]["categories"]
        if not pred_channels:
            return _article

        pred_channels = sorted(
            pred_channels, key=lambda d: d["confidence"], reverse=True
        )[0]

        # Skip article if predicted channel is in excluded channels or if confidence is below threshold
        if (
            pred_channels["name"] in config.nu_excluded_channels
            or pred_channels["confidence"] < config.nu_confidence_threshold
        ):
            return _article

        # If article in augmented channels, only replace non-augmented channels with predicted channel
        to_augment = list(
            set(_article["channels"]).intersection(config.nu_augment_channels)
        )
        if to_augment:
            _article["channels"] = [pred_channels["name"]] + to_augment
            return _article

        # otherwise replace article channels with predicted channel
        _article["channels"] = [pred_channels["name"]]
        return _article

    except Exception as e:
        logger.error(f"Unable to get predicted category for {_article} due to {e}")
        return _article


def get_external_predicted_channels(text_content, language="en"):
    """
    Classifying Content in a String

    Args:
      text_content The text content to analyze.
    """

    # Available types: PLAIN_TEXT, HTML
    type_ = language_v1.Document.Type.PLAIN_TEXT

    document = {"content": text_content, "type_": type_, "language": language}

    content_categories_version = (
        language_v1.ClassificationModelOptions.V2Model.ContentCategoriesVersion.V2
    )
    try:
        response = client.classify_text(
            request={
                "document": document,
                "classification_model_options": {
                    "v2_model": {
                        "content_categories_version": content_categories_version
                    }
                },
            }
        )
    except Exception as e:
        print(e)
        return []

    return response.categories


def get_external_channels_for_article(article):
    raw_data = get_external_predicted_channels(
        article["description"] + " " + article["title"]
    )

    return get_channels_for_classification(raw_data)
