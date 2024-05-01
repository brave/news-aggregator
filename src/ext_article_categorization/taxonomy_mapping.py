from functools import lru_cache

from config import get_config

config = get_config()


BRAVE_V1_TO_EXTERNAL_TAXONOMY = {
    "Business": [
        "/Business & Industrial/Business*",
        "/Finance*",
        "/News/Business News*",
        "/People & Society/Social Sciences/Economics",
    ],
    "Cars": ["/Autos & Vehicles/Motor Vehicles*"],
    "Celebrities": ["/Arts & Entertainment/Celebrities & Entertainment News"],
    "Education": [
        "/Jobs & Education/Education*",
        "/Reference/General Reference/Educational Resources",
    ],
    "Entertainment": ["/Arts & Entertainment*"],
    "Fashion": ["/Beauty & Fitness/Fashion & Style*"],
    "Film and TV": [
        "/Arts & Entertainment/Movies*",
        "/Arts & Entertainment/Entertainment Industry/Film & TV Industry",
        "/Arts & Entertainment/Events & Listings/Film Festivals",
        "/Arts & Entertainment/TV & Video*",
    ],
    "Food": [
        "/Food & Drink*",
        "/Arts & Entertainment/Events & Listings/Food & Beverage Events",
    ],
    "Gaming": ["/Games/Computer & Video Games*"],
    "Health": [
        "/Health*",
        "/Beauty & Fitness/Fitness*",
        "/Food & Drink/Cooking & Recipes/Healthy Eating",
        "/News/Health News",
        "/People & Society/Social Sciences/Psychology",
    ],
    "Home": [
        "/Home & Garden*",
        "/Computers & Electronics/Consumer Electronics/Home Automation",
    ],
    "Lifestyle": [
        "~Travel",
        "/Arts & Entertainment/Visual Art & Design/Architecture",
        "/Arts & Entertainment/Visual Art & Design/Design",
        "/Home & Garden/Home & Interior Decor",
        "/Shopping/Luxury Goods",
        "/Travel & Transportation/Tourist Destinations*",
        "/Food & Drink/Restaurants/Fine Dining",
        "/Beauty & Fitness/Fashion & Style/Fashion Designers & Collections",
    ],
    "Music": [
        "/Arts & Entertainment/Music*",
        "/Arts & Entertainment/Events & Listings/Concerts & Music Festivals",
    ],
    "Politics": ["/News/Politics*"],
    "Science": ["/Science*"],
    "Sports": ["/Sports*", "/News/Sports News"],
    "Technology": [
        "/Computers & Electronics*",
        "/Internet & Telecom*",
        "/News/Technology News",
        "/Online Communities/Social Networks",
        "/Science/Computer Science/Machine Learning & Artificial Intelligence",
        "/Business & Industrial/Aerospace & Defense/Space Technology",
    ],
    "Travel": [
        "/Travel & Transportation/Luggage & Travel Accessories*",
        "/Travel & Transportation/Specialty Travel*",
        "/Travel & Transportation/Tourist Destinations*",
        "/Travel & Transportation/Travel Agencies & Services*",
    ],
    "Weather": ["/News/Weather"],
    "World News": ["/News/World News*"],
    "*Offers": ["/Shopping/Consumer Resources/Coupons & Discount Offers"],
    "*Adult": ["/Adult"],
    "*Sensitive": ["/Sensitive Subjects*"],
    "*Religion": ["/People & Society/Religion & Belief"],
}

EXTERNAL_AUGMENT_CHANNELS = ["Crypto", "Culture", "Brave", "Top News", "Top Sources"]
EXTERNAL_DEFAULT_CHANNELS = ["Fun"]


@lru_cache(maxsize=None)
def get_external_to_brave_v1_taxonomy():
    with open(config.taxonomy_v1_file, "r") as f:
        gcloud_taxonomy = f.readlines()

    # Invert and expand mapping
    external_to_brave_v1_taxonomy = {}
    for b_channel, g_categories in BRAVE_V1_TO_EXTERNAL_TAXONOMY.items():
        for g_category in g_categories:
            if g_category.startswith("~"):
                # TODO: support importing entire channels here
                continue

            if g_category.endswith("*"):
                # find all categories that start with this
                g_category = g_category[:-1]
                for category in gcloud_taxonomy:
                    category = category.strip()
                    if category.startswith(g_category):
                        if g_category not in external_to_brave_v1_taxonomy:
                            external_to_brave_v1_taxonomy[category] = []
                        external_to_brave_v1_taxonomy[category].append(b_channel)
            else:
                if g_category not in external_to_brave_v1_taxonomy:
                    external_to_brave_v1_taxonomy[g_category] = []
                external_to_brave_v1_taxonomy[g_category].append(b_channel)

    return external_to_brave_v1_taxonomy


def get_channels_for_classification(categories):
    external_to_brave_v1_taxonomy = get_external_to_brave_v1_taxonomy()
    channels = []
    for category in categories:
        if category.confidence < 0.2:
            continue

        g_category = category.name.strip()
        if g_category in external_to_brave_v1_taxonomy:
            channels.extend(external_to_brave_v1_taxonomy[g_category])

    return list(set(channels))
