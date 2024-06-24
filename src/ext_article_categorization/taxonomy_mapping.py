"""
Mappings go from external categories to internal categories, which are divided into two tiers.
Tier 2 categories are more specific, while Tier 1 categories are more general.
The mappings are used to determine the Tier 1 and Tier 2 categories for an article.
Mappings have the following notation:
$high_level_channel: [$lower_level_channel, $lower_level_channel_2, ...]
Lower level channels can have the following notation:
- "category_or_channel_name": Include only this channel
- "category_or_channel_prefix*": Include all categories/channels that start with category_or_channel_prefix
- "-category_or_channel_name": If this category/channel is found, exclude it from the higher_level_channel
"""

from config import get_config

config = get_config()

TIER_2_TO_EXTERNAL_MAPPING = {
    # Business
    "Companies": ["/News/Business News/Company News"],
    "Economy": [
        "/News/Business News/Economy News",
        "/People & Society/Social Sciences/Economics",
        "/People & Society/Social Issues & Advocacy/Work & Labor Issues",
    ],
    "Finance": ["/Finance*", "/News/Business News/Financial Markets News"],
    "Stocks & Investing": ["Finance/Investing*"],
    "Real Estate": ["/Real Estate*"],
    # Arts, Culture & Entertainment
    "Art & Design": ["/Arts & Entertainment/Visual Art & Design*"],
    "Books": ["/Books & Literature*"],
    "Celebrities": ["/News/Gossip & Tabloid News/Other"],
    "Comics": ["/Arts & Entertainment/Comics & Animation*"],
    "Culture": ["/People & Society/Social Issues & Advocacy*"],
    "Gaming": [
        "/Games/Computer & Video Games*",
        "/Computers & Electronics/Consumer Electronics/Game Systems & Consoles",
    ],
    "Film and TV": [
        "/Arts & Entertainment/Movies*",
        "/Arts & Entertainment/TV & Video/TV Shows & Programs",
        "/Arts & Entertainment/TV & Video/Online Video",
        "/Arts & Entertainment/Entertainment Industry/Film & TV Industry",
        "/Arts & Entertainment/Events & Listings/Film Festivals",
        "-/Arts & Entertainment/Movies/Other",
    ],
    "Music": [
        "/Arts & Entertainment/Music & Audio*",
        "/Arts & Entertainment/Events & Listings/Concerts & Music Festivals",
        "-/Arts & Entertainment/Music & Audio/Podcasts",
    ],
    "Architecture": ["/Arts & Entertainment/Visual Art & Design/Architecture"],
    "Humor": ["/Arts & Entertainment/Humor*"],
    "Fun & Trivia": [
        "/Arts & Entertainment/Fun & Trivia*",
        "/Games/Puzzles & Brainteasers",
    ],
    "Performing Arts": ["/Arts & Entertainment/Performing Arts*"],
    # Lifestyle
    "Fashion": ["/Beauty & Fitness/Fashion & Style*"],
    "Food & Drink": [
        "/Food & Drink*",
        "/Arts & Entertainment/Events & Listings/Food & Beverage Events",
    ],
    "Health & Fitness": [
        "/Beauty & Fitness/Fitness*",
        "/Food & Drink/Cooking & Recipes/Healthy Eating",
        "/News/Health News",
        "/Beauty & Fitness/Face & Body Care*",
        "/People & Society/Social Sciences/Psychology",
        "/Health/Nutrition*",
    ],
    "Home & Garden": [
        "/Home & Garden*",
        "/Computers & Electronics/Consumer Electronics/Home Automation",
    ],
    "Travel": [
        "/Travel & Transportation/Specialty Travel*",
        "/Travel & Transportation/Tourist Destinations*",
        "/Travel & Transportation/Travel Guides & Travelogues",
    ],
    "Education": [
        "/Jobs & Education/Education*",
        "/People & Society/Self-Help & Motivational",
        "/Arts & Entertainment/Music & Audio/Music Education & Instruction",
        "/Reference/General Reference/Educational Resources",
    ],
    "Relationships": [
        "/People & Society/Family & Relationships*",
        "/Hobbies & Leisure/Special Occasions/Weddings",
    ],
    "Pets": ["/Pets & Animals*"],
    "Medical": ["/Health*"],
    # Technology
    "Consumer Electronics": [
        "/Computers & Electronics/Consumer Electronics*",
        "-/Computers & Electronics/Consumer Electronics/Game Systems & Consoles",
    ],
    "Internet": [
        "/Internet & Telecom*",
        "/Computers & Electronics/Computer Security*",
        "/Computers & Electronics/Networking",
    ],
    "Gadgets": [
        "/Computers & Electronics/Consumer Electronics*",
        "-/Computers & Electronics/Consumer Electronics/Game Systems & Consoles",
    ],
    "Software": ["/Computers & Electronics/Software*"],
    "Artificial Intelligence": [
        "/Science/Computer Science/Machine Learning & Artificial Intelligence"
    ],
    # Sports
    "American Football": ["/Sports/Team Sports/American Football"],
    "Football": ["/Sports/Team Sports/Soccer"],
    "Basketball": ["/Sports/Team Sports/Basketball"],
    "Baseball": ["/Sports/Team Sports/Baseball"],
    "Hockey": ["/Sports/Team Sports/Hockey"],
    "Golf": ["/Sports/Individual Sports/Golf"],
    "Cricket": ["/Sports/Team Sports/Cricket"],
    "Tennis": ["/Sports/Individual Sports/Tennis"],
    "Rugby": ["/Sports/Team Sports/Rugby"],
    "Motorsports": ["/Sports/Motor Sports*"],
    "Combat": ["/Sports/Combat Sports*"],
    # Science
    "Space": ["/Science/Astronomy"],
    "Environment": ["/Science/Earth Sciences/Environmental Science"],
    "Physics": ["/Science/Physics"],
    "Biology": ["/Science/Biological Sciences*"],
    # Sensitive
    "War": ["/Sensitive Subjects/War & Conflict"],
    "Drugs": ["/Sensitive Subjects/Recreational Drugs"],
    # Others
    "Royals": ["/Law & Government/Government/Royalty"],
    "Elections": ["/News/Politics/Campaigns & Elections"],
}

# Tier 1 should be mapped either to a tier 2 or a gcloud category (no Tier 1)
TIER_1_TO_TIER_2_MAPPING = {
    "Business": [
        "Companies",
        "Finance",
        "Economy",
        "Stocks & Investing",
        "Personal Finance",
        "Real Estate",
        "/News/Business News*",
    ],
    "Arts & Entertainment": [
        "Art & Design",
        "Books",
        "Comics",
        "Film and TV",
        "Music",
        "Architecture",
        "Humor",
        "Performing Arts",
    ],
    "Gaming": ["Gaming"],
    "Lifestyle": [
        "Fashion",
        "Food & Drink",
        "Health & Fitness",
        "Home & Garden",
        "Travel",
        "Education",
        "Relationships",
        "Pets",
    ],
    "Technology": [
        "Consumer Electronics",
        "Internet",
        "Gadgets",
        "Software",
        "Artificial Intelligence",
        "/News/Technology News",
        "/Business & Industrial/Aerospace & Defense/Space Technology",
    ],
    "Sports": [
        "Football",
        "Basketball",
        "Baseball",
        "Hockey",
        "Golf",
        "Cricket",
        "Tennis",
        "Rugby",
        "Motorsports",
        "Combat",
        "American Football",
        "/Sports*",
        "/News/Sports News",
    ],
    "Science": ["Space", "Environment", "Physics", "Biology", "/Science*"],
    # Others
    "Cars": ["/Autos & Vehicles/Motor Vehicles*"],
    "Celebrities": ["Celebrities", "Royals", "-/News/Politics*"],
    "Culture": ["Culture"],
    "Politics": ["Elections", "/News/Politics*"],
    "Weather": ["/News/Weather"],
    "World News": ["/News/World News"],
    "*Reviews": ["/Shopping/Consumer Resources/Product Reviews & Price Comparisons"],
    "*Offers": ["/Shopping/Consumer Resources/Coupons & Discount Offers"],
    "*Adult": ["/Adult"],
    "*Sensitive": ["War", "Drugs", "/Sensitive Subjects*"],
    "*Belief": ["/People & Society/Religion & Belief"],
}

EXTERNAL_AUGMENT_CHANNELS = ["Crypto", "Culture", "Brave", "Top News", "Top Sources"]
EXTERNAL_DEFAULT_CHANNELS = ["Fun"]

with open("data/gcloud_taxonomy.txt", "r") as f:
    gcloud_taxonomy = f.readlines()


def process_taxonomy(tier_mapping, gcloud_taxonomy, exclusions, taxonomy):
    """
    Process the taxonomy mapping and generates the inverse taxonomy mapping as dictionary.

    Args:
      tier_mapping (dict): The mapping of lower tier categories to higher tier categories.
      gcloud_taxonomy (list): The list of categories from the Google Cloud taxonomy.
      exclusions (dict): The exclusion rules for the mapping.
      taxonomy (dict): The resulting taxonomy dictionary.

    Returns:
      Update exclusions and taxonomy dictionaries.
    """
    for tier, categories in tier_mapping.items():
        for category in categories:
            category = category.strip()
            # Setup exclusion
            if category.startswith("-"):
                category = category[1:]
                if category.endswith("*"):
                    category = category[:-1]
                    for g_category in gcloud_taxonomy:
                        g_category = g_category.strip()
                        if g_category.startswith(category):
                            exclusions.setdefault(category, []).append(tier)
                else:
                    exclusions.setdefault(category, []).append(tier)
            # Add all with prefix
            elif category.endswith("*"):
                category_prefix = category[:-1]
                for g_category in gcloud_taxonomy:
                    g_category = g_category.strip()
                    if g_category.startswith(category_prefix):
                        taxonomy.setdefault(g_category, []).append(tier)
            # Add only this category
            else:
                taxonomy.setdefault(category, []).append(tier)


tier_2_exclusions = {}
external_to_tier2_taxonomy = {}
process_taxonomy(
    TIER_2_TO_EXTERNAL_MAPPING,
    gcloud_taxonomy,
    tier_2_exclusions,
    external_to_tier2_taxonomy,
)

tier_1_exclusions = {}
tier_2_to_tier_1_taxonomy = {}
process_taxonomy(
    TIER_1_TO_TIER_2_MAPPING,
    gcloud_taxonomy,
    tier_1_exclusions,
    tier_2_to_tier_1_taxonomy,
)


def process_categories(categories, taxonomy, exclusions):
    """
    Process the categories and generate the corresponding tiers.

    Args:
      categories (list): The list of categories to process.
      taxonomy (dict): The taxonomy dictionary.
      exclusions (dict): The exclusion rules for the taxonomy.

    Returns:
      list: The list of higher tier categories/channels for the given categories.
    """
    higher_tier = []
    for category in categories:
        if category in taxonomy:
            temp_tiers = taxonomy[category]
            if category in exclusions:
                for exclusion in exclusions[category]:
                    if exclusion in temp_tiers:
                        temp_tiers.remove(exclusion)
            higher_tier.extend(temp_tiers)
    return higher_tier


def get_channels_for_classification(categories):
    tier_2s = []
    tier_1s = []
    for category_result in categories:
        category = category_result.name
        score = category_result.confidence
        if score < 0.15:
            continue

        g_category = category.strip()
        # Fill in the tier 2 and tier 1 categories from external classification
        tier_2s.extend(
            process_categories(
                [g_category], external_to_tier2_taxonomy, tier_2_exclusions
            )
        )
        tier_1s.extend(
            process_categories(
                [g_category], tier_2_to_tier_1_taxonomy, tier_1_exclusions
            )
        )

    for tier_2 in tier_2s:
        # Fill in the tier 1 categories from the tier 2 categories
        tier_1s.extend(
            process_categories([tier_2], tier_2_to_tier_1_taxonomy, tier_1_exclusions)
        )

    return {"tier_2": list(set(tier_2s)), "tier_1": list(set(tier_1s))}
