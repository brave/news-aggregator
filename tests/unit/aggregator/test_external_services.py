from aggregator.external_services import get_popularity_score, get_predicted_channels
from config import get_config

config = get_config()


class TestGetPopularityScore:
    # Successfully retrieves popularity score for an article.
    def test_retrieves_popularity_score(self, mocker):
        # Mock the get_with_max_size function to return a sample response
        mocker.patch(
            "aggregator.external_services.get_with_max_size",
            return_value=b'{"popularity": {"popularity": {"score1": 1, "score2": 2}}}',
        )

        # Create a sample article
        out_article = {
            "url": "https://example.com/article",
            "title": "Example Article",
            "author": "John Doe",
            "publish_time": "2022-01-01T12:00:00Z",
        }

        # Call the get_popularity_score function
        result = get_popularity_score(out_article)

        # Assert that the popularity score is None
        assert result["pop_score"] == 3

    # URL is invalid or empty.
    def test_invalid_or_empty_url(self, mocker):
        # Mock the get_with_max_size function to raise an exception
        mocker.patch(
            "aggregator.external_services.get_with_max_size",
            side_effect=ValueError("Content-Length too large"),
        )

        # Create a sample article with an invalid URL
        out_article = {
            "url": "",
            "title": "Example Article",
            "author": "John Doe",
            "publish_time": "2022-01-01T12:00:00Z",
        }

        # Call the get_popularity_score function
        result = get_popularity_score(out_article)

        # Assert that the popularity score is 1.0
        assert result["pop_score"] == 1.0


class TestGetPredictedChannel:
    def test_article_default_channel_or_short_text(self, mocker):
        mocker.patch("requests.post")
        mocker.patch("structlog.getLogger")

        channels_1_default = ["Fun"]
        channels_2 = ["Sports"]

        article_1 = {
            "channels": channels_1_default,
            "title": "This is a title",
            "description": "This is an article description",
        }

        article_2 = {
            "channels": channels_2,
            "title": "Short",
            "description": "",
        }

        result_1 = get_predicted_channels(article_1)
        result_2 = get_predicted_channels(article_2)

        assert result_1["channels"] == channels_1_default
        assert result_2["channels"] == channels_2

    def test_article_api_response_no_categories(self, mocker):
        # Mock the necessary dependencies
        mock_post = mocker.patch("requests.post")
        mock_post.return_value.raise_for_status.return_value = None
        mock_post.return_value.json.return_value = {"results": [{"categories": []}]}
        mocker.patch("structlog.getLogger")

        channels = ["channel1", "channel2"]

        article = {
            "channels": channels,
            "title": "This is a title",
            "description": "This is an article description",
        }

        result = get_predicted_channels(article)

        assert result["channels"] == channels

    def test_article_if_predicted_category_excluded(self, mocker):
        # Mock the necessary dependencies
        mock_post = mocker.patch("requests.post")
        mock_post.return_value.raise_for_status.return_value = None
        excluded_category = "Crime"
        mock_post.return_value.json.return_value = {
            "results": [
                {
                    "categories": [
                        {
                            "name": excluded_category,
                            "confidence": config.nu_confidence_threshold,
                        }
                    ]
                }
            ]
        }
        mocker.patch("structlog.getLogger")

        article = {
            "channels": ["channel1", "channel2"],
            "title": "This is a title",
            "description": "This is an article description",
        }

        result = get_predicted_channels(article)

        assert excluded_category not in result["channels"]

    def test_article_if_predicted_category_below_threshold(self, mocker):
        # Mock the necessary dependencies
        mock_post = mocker.patch("requests.post")
        mock_post.return_value.raise_for_status.return_value = None
        valid_category = "Sports"
        mock_post.return_value.json.return_value = {
            "results": [
                {
                    "categories": [
                        {
                            "name": valid_category,
                            "confidence": config.nu_confidence_threshold / 2,
                        }
                    ]
                }
            ]
        }
        mocker.patch("structlog.getLogger")

        article = {
            "channels": ["channel1", "channel2"],
            "title": "This is an article title",
            "description": "This is an article description",
        }

        result = get_predicted_channels(article)

        assert valid_category not in result["channels"]

    def test_predict_channel(self, mocker):
        mock_post = mocker.patch("requests.post")
        mock_post.return_value.raise_for_status.return_value = None
        valid_category = "Sports"
        mock_post.return_value.json.return_value = {
            "results": [
                {
                    "categories": [
                        {
                            "name": valid_category,
                            "confidence": config.nu_confidence_threshold,
                        }
                    ]
                }
            ]
        }
        mocker.patch("structlog.getLogger")

        article = {
            "channels": ["channel1", "channel2"],
            "title": "This is an article title",
            "description": "This is an article description",
        }

        result = get_predicted_channels(article)

        assert result["channels"] == [valid_category]

    def test_predict_channel_with_augment_channel(self, mocker):
        mock_post = mocker.patch("requests.post")
        mock_post.return_value.raise_for_status.return_value = None
        valid_category = "Sports"
        mock_post.return_value.json.return_value = {
            "results": [
                {
                    "categories": [
                        {
                            "name": valid_category,
                            "confidence": config.nu_confidence_threshold,
                        }
                    ]
                }
            ]
        }
        mocker.patch("structlog.getLogger")

        article_1 = {
            "channels": ["Politics", "Top Sources"],
            "title": "This is an article title",
            "description": "This is an article description",
        }

        article_2 = {
            "channels": ["Top News", "Top Sources"],
            "title": "This is an article title",
            "description": "This is an article description",
        }

        result_1 = get_predicted_channels(article_1)
        result_2 = get_predicted_channels(article_2)

        assert set(result_1["channels"]) == set(["Top Sources", valid_category])
        assert set(result_2["channels"]) == {"Top News", "Top Sources", valid_category}

    def test_predict_channel_with_default_channel(self, mocker):
        mock_post = mocker.patch("requests.post")
        mock_post.return_value.raise_for_status.return_value = None
        valid_category = "Sports"
        mock_post.return_value.json.return_value = {
            "results": [
                {
                    "categories": [
                        {
                            "name": valid_category,
                            "confidence": config.nu_confidence_threshold,
                        }
                    ]
                }
            ]
        }
        mocker.patch("structlog.getLogger")

        article_1 = {
            "channels": ["Fun", "Top Sources"],
            "title": "This is an article title",
            "description": "This is an article description",
        }

        article_2 = {
            "channels": ["Fun"],
            "title": "This is an article title",
            "description": "This is an article description",
        }

        result_1 = get_predicted_channels(article_1)
        result_2 = get_predicted_channels(article_2)

        assert set(result_1["channels"]) == set(["Top Sources", "Fun"])
        assert set(result_2["channels"]) == set(["Fun"])
