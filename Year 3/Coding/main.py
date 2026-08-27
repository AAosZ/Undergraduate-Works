import pandas as pd
import re
from word2number import w2n
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

numbers = {
    "cent": 0.01,
    "cents": 0.01,
    "hundred": 100,
    "k": 1000,
    "thousand": 1000,
    "m": 1000000,
    "million": 1000000,
    "b": 1000000000,
    "billion": 1000000000
}

# For the word2number import. We do not want these words to turn into their
# values standalone
blacklist = {
    "hundred",
    "thousand",
    "million",
    "billion"
}

blacklist2 = {
    "few",
    "some",
    "several",
    "many",
    "couple",
    "various",
    "multiple"
}



# These are the values you can change

remove_percent = 0.5 # all rows that have less than remove_percent % of their data is removed.

# Extreme outlier management - cap values to prevent negatively affecting the model learning or do not provide any meaningful information
maximum_cutoff = 1000000000 # Cap the value of the painting for anyone who dare says they will pay over maximum_cutoff dollars for a painting (PAINTING VALUE ONLY)
character_cutoff = 3 # Cut anyone that was lazy enough to respond with less than character_cutoff number of characters NOT INCLUSIVE (ANY TEXT FEATURE ONLY)
max_colours = 50 # cap anyone that says they saw more than max_colours colours in a painting
max_objects = 50 # cap anyone that says they saw more than max_objects objects in a painting



dataset = pd.read_csv("ml_challenge_dataset.csv")


# ---------------------------------------------------------------------------------
# Removing useless rows

# removes all rows with more than remove_percent * (len(dataset.columns) - 2) missing features.
removal_threshold = int(remove_percent * (len(dataset.columns) - 2))
dataset_v1 = dataset.dropna(axis=0, thresh=removal_threshold)



# ---------------------------------------------------------------------------------
# Ensures numeric features (formerly considered objects) is completely numeric

def parse_value(text):

    text = text_normalize(text)

    if text == "":
        return np.nan

    nums = find_value(text)

    if nums:
        # Cut all responses with overly exaggerated values.
        if find_range(nums) > maximum_cutoff:
            return np.nan
        return find_range(nums)

    word_val = textparser(text)

    if word_val:
        return word_val

    return np.nan


# Helper function land

def text_normalize(text):
    if pd.isna(text):
        return ""

    # Ignore this lmao
    text = str(text).lower()
    text = text.replace("$", "")
    text = text.replace(",", "")
    text = text.replace("Â", "")
    text = text.replace("'", "")
    text = text.replace("€", "")
    text = text.replace("(", "")
    text = text.replace(")", "")
    text = text.replace(":", "")
    text = text.replace("?", "")
    text = text.replace("~", "")
    text = text.replace("`", "")
    text = text.replace("â", "")
    text = text.replace("™", "")
    text = text.replace("Â", "")

    text = text.strip()

    return text


def find_value(text):
    # This uses regex to parse the value of the painting out of the text.
    # People responded in a variety of ways that I would colourfully describe.

    # Remove spaces in numbers
    text = re.sub(r'(\d+)\s+(?=\d)', r'\1', text)

    # Actual parser
    regex = r'\d+(?:\.\d+)?(?:cent|cents|hundred|k|thousand|m|million|b|billion)?'

    matches = re.findall(regex, text)

    if not matches:
        return None

    nums = []

    for match in matches:
        num = re.match(r'\d+(?:\.\d+)?', match).group()
        value = float(num)

        suffix = match[len(num):]

        if suffix in numbers:
            value *= numbers[suffix]

        nums.append(value)

    return nums


def find_range(nums):
    # We average any range of values in the dataset
    if len(nums) == 2:
        return sum(nums[:2]) / 2

    # If someone is indecisive, remove their response. For example,

    # "That depends, if I were a billionaire, probably 100 million, but because
    # I'm not, probably $5000 max since I know how valuable this painting is.
    # Otherwise, if this painting wasn't valuable, max $500."

    # Yes, this was a real response in the dataset.
    elif len(nums) > 2:
        return np.nan

    return nums[0]


def textparser(text):
    # In case someone used only words to describe what they want to pay for the painting.
    words = text.split()

    if len(words) == 1 and words[0] in blacklist:
        return None

    if any(word in blacklist for word in words):
        return None

    try:
        return w2n.word_to_num(text)
    except:
        return None


def cap_values(value):
    if pd.isna(value):
        return np.nan

    if value > max_colours or value > max_objects:
        return np.nan
    else:
        return value


# End Helper function land



# Clean up the painting value column
value_feature = "How much (in Canadian dollars) would you be willing to pay for this painting?"
dataset_v1[value_feature] = dataset_v1[value_feature].apply(parse_value)
dataset_v1[value_feature] = pd.to_numeric(dataset_v1[value_feature], errors="coerce")

# Leave only the numeric values for the features that ask for agreement or disagreement.
to_be_cleaned = [
    "This art piece makes me feel sombre.",
    "This art piece makes me feel content.",
    "This art piece makes me feel calm.",
    "This art piece makes me feel uneasy."
]

for column in to_be_cleaned:
    dataset_v1[column] = dataset_v1[column].apply(parse_value)
    dataset_v1[column] = pd.to_numeric(dataset_v1[column], errors="coerce")

# Anyone who says they see 51 or more objects or PROMINENT colours is capping (I'm being very lenient here)
cap_features = [
    "How many prominent colours do you notice in this painting?",
    "How many objects caught your eye in the painting?"
]

for column in cap_features:
    dataset_v1[column] = dataset_v1[column].apply(cap_values)
    dataset_v1[column] = pd.to_numeric(dataset_v1[column], errors="coerce")

# We permute missing numerical features with the following
# THIS CAN BE CHANGED - ANY NUMERICAL FEATURE ROWS WITH MISSING VALUES ARE ASSIGNED THE MEDIAN VALUE OF ALL RESPONSES
numeric_cols = dataset_v1.select_dtypes(include=['number']).columns
dataset_v1[numeric_cols] = dataset_v1[numeric_cols].fillna(dataset_v1[numeric_cols].median())

# ---------------------------------------------------------------------------------

# Clean up all text features

def clean_text_column(text):
    """
    Clean text data by fixing encoding issues and removing corrupted responses
    """
    # Return NaN for missing values
    if pd.isna(text):
        return np.nan

    text = str(text)

    text = text.replace("Â", "")
    text = text.replace("â", "")

    # Remove extra whitespace
    text = ' '.join(text.split())

    # Remove any responses less than character_cutoff long
    if len(text) < character_cutoff:
        return np.nan

    return text

# This is needed because some dude's responses were encoded so badly that even pycharm couldn't read it
def detect_corrupted_text(text):
    if pd.isna(text):
        return True

    text = str(text)

    # Calculate ratio of ASCII vs non-ASCII characters
    ascii_chars = sum(1 for char in text if ord(char) < 128)
    total_chars = len(text)

    if total_chars == 0:
        return True

    ascii_ratio = ascii_chars / total_chars

    if ascii_ratio < 0.9:
        return True

    # Check for common mojibake patterns
    mojibake_patterns = ['å', 'æ', 'œ', '€', 'â', 'ç', 'è', 'é', 'ê', 'ë', 'ï', 'î', 'ô', 'ù', 'û', 'ü']
    mojibake_count = sum(1 for pattern in mojibake_patterns if pattern in text)

    if mojibake_count > 3:
        return True

    return False

def clean_text_columns(dataset, text_columns):
    for col in text_columns:
        if col in dataset.columns:
            corrupted_mask = dataset[col].apply(detect_corrupted_text)
            dataset.loc[corrupted_mask, col] = np.nan

            dataset[col] = dataset[col].apply(clean_text_column)

    return dataset

text_columns = [
    'Describe how this painting makes you feel.',
    'If this painting was a food, what would be?',
    'Imagine a soundtrack for this painting. Describe that soundtrack without naming any objects in the painting.'
]

dataset_v2 = clean_text_columns(dataset_v1, text_columns)



dataset_v2.to_csv('cleaned_MLCHALLENGE_dataset.csv', index=False)


# Load the cleaned dataset
# df = pd.read_csv("cleaned_MLCHALLENGE_dataset.csv")
#
# # Filter out extreme outliers for better visualization (optional)
# price_data = []
# paintings = ["The Persistence of Memory", "The Starry Night", "The Water Lily Pond"]
#
# for painting in paintings:
#     prices = df[df["Painting"] == painting]["How much (in Canadian dollars) would you be willing to pay for this painting?"]
#     # Cap at 1 million for visualization (your code already caps at 1B)
#     prices_capped = prices[prices <= 1_000_000_000]
#     price_data.append(prices_capped)
#
# # Create the boxplot
# fig, ax = plt.subplots(figsize=(10, 6))
# bp = ax.boxplot(price_data, labels=paintings, patch_artist=True)
#
# # Customize colors
# colors = ['#FF9999', '#99FF99', '#9999FF']
# for patch, color in zip(bp['boxes'], colors):
#     patch.set_facecolor(color)
#
# ax.set_ylabel("Price Willing to Pay (CAD)", fontsize=12)
# ax.set_title("Distribution of Willingness to Pay by Painting", fontsize=14)
# ax.set_yscale('log')  # Log scale because of extreme outliers
# ax.set_ylim(1, 1_000_000)
#
# # Add statistical annotations
# for i, painting in enumerate(paintings):
#     prices = price_data[i]
#     median = prices.median()
#     q1, q3 = prices.quantile(0.25), prices.quantile(0.75)
#     ax.text(i+1, median * 1.5, f'Median: ${median:.0f}', ha='center', fontsize=9)
#
# plt.tight_layout()
# plt.savefig('price_distribution.png', dpi=150)
# plt.show()
#
# # Print statistics for your write-up
# print("\n=== Price Statistics by Painting ===")
# for i, painting in enumerate(paintings):
#     prices = price_data[i]
#     print(f"\n{painting}:")
#     print(f"  Mean: ${prices.mean():.0f}")
#     print(f"  Median: ${prices.median():.0f}")
#     print(f"  Std Dev: ${prices.std():.0f}")
#     print(f"  IQR: ${prices.quantile(0.75) - prices.quantile(0.25):.0f}")
#
#
#
# # Figure 2: Multiple numerical features boxplots
# fig, axes = plt.subplots(2, 3, figsize=(15, 10))
# features = [
#     ("On a scale of 1–10, how intense is the emotion conveyed by the artwork?", "Emotion Intensity"),
#     ("How many prominent colours do you notice in this painting?", "Prominent Colours"),
#     ("How many objects caught your eye in the painting?", "Objects Noticed"),
#     ("This art piece makes me feel sombre.", "Sombre (1-5)"),
#     ("This art piece makes me feel content.", "Content (1-5)"),
#     ("This art piece makes me feel calm.", "Calm (1-5)")
# ]
#
# paintings = df["Painting"].unique()
# colors = ['#FF9999', '#99FF99', '#9999FF']
#
# for idx, (col, title) in enumerate(features):
#     ax = axes[idx // 3, idx % 3]
#
#     data = []
#     for painting in paintings:
#         values = df[df["Painting"] == painting][col].dropna()
#         data.append(values)
#
#     bp = ax.boxplot(data, labels=paintings, patch_artist=True)
#     for patch, color in zip(bp['boxes'], colors):
#         patch.set_facecolor(color)
#
#     ax.set_title(title, fontsize=11)
#     ax.set_ylabel("Value")
#
#     # Add annotation for class separation
#     means = [d.mean() for d in data]
#     if max(means) - min(means) > 0.5:
#         ax.text(0.02, 0.95, "✓ Separated", transform=ax.transAxes,
#                 fontsize=9, color='green', fontweight='bold')
#     else:
#         ax.text(0.02, 0.95, "○ Overlapping", transform=ax.transAxes,
#                 fontsize=9, color='red', fontweight='bold')
#
# plt.tight_layout()
# plt.savefig('numerical_features_comparison.png', dpi=150)
# plt.show()
#
# # Calculate discriminative power for each feature
# print("\n=== Feature Discriminative Power (ANOVA F-statistic) ===")
#
# for col, title in features:
#     groups = [df[df["Painting"] == p][col].dropna().values for p in paintings]
#     # Remove empty groups
#     groups = [g for g in groups if len(g) > 0]
#     if len(groups) >= 2:
#         f_stat, p_val = stats.f_oneway(*groups)
#         print(f"{title:30} F={f_stat:.2f}, p={p_val:.4f}")
#
#
# # Figure 3: Categorical features - stacked bar charts
# fig, axes = plt.subplots(1, 3, figsize=(15, 5))
#
# categorical_features = [
#     ("If you could purchase this painting, which room would you put that painting in?", "Room"),
#     ("If you could view this art in person, who would you want to view it with?", "Company"),
#     ("What season does this art piece remind you of?", "Season")
# ]
#
# for idx, (col, title) in enumerate(categorical_features):
#     ax = axes[idx]
#
#     # Create crosstab
#     crosstab = pd.crosstab(df["Painting"], df[col], normalize='index') * 100
#
#     # Plot stacked bars
#     crosstab.plot(kind='bar', stacked=True, ax=ax, colormap='viridis', edgecolor='black')
#
#     ax.set_title(f"{title} Distribution by Painting", fontsize=12)
#     ax.set_ylabel("Percentage (%)")
#     ax.set_xlabel("")
#     ax.legend(loc='center left', bbox_to_anchor=(1, 0.5), fontsize=8)
#     ax.tick_params(axis='x', rotation=15)
#
#     # Add Chi-square annotation
#     contingency = pd.crosstab(df["Painting"], df[col])
#     chi2, p, dof, expected = stats.chi2_contingency(contingency)
#     significance = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else "ns"
#     ax.text(0.02, 0.95, f"χ²={chi2:.1f}{significance}", transform=ax.transAxes,
#             fontsize=9, verticalalignment='top')
#
# plt.tight_layout()
# plt.savefig('categorical_features.png', dpi=150, bbox_inches='tight')
# plt.show()
#
# # Print detailed statistics
# print("\n=== Categorical Feature Statistics ===")
# for col, title in categorical_features:
#     contingency = pd.crosstab(df["Painting"], df[col])
#     chi2, p, dof, expected = stats.chi2_contingency(contingency)
#     cramers_v = np.sqrt(chi2 / (len(df) * (min(contingency.shape) - 1)))
#     print(f"\n{title}:")
#     print(f"  Chi-square: {chi2:.2f}")
#     print(f"  P-value: {p:.4f}")
#     print(f"  Cramér's V: {cramers_v:.3f}")  # 0=no association, 1=perfect association
#
#
#
# # Figure 4: Word distinctiveness for text features
# from collections import Counter
# import matplotlib.pyplot as plt
#
# text_columns = [
#     'Describe how this painting makes you feel.',
#     'If this painting was a food, what would be?',
#     'Imagine a soundtrack for this painting. Describe that soundtrack without naming any objects in the painting.'
# ]
#
# fig, axes = plt.subplots(1, 3, figsize=(18, 6))
#
# for idx, col in enumerate(text_columns):
#     ax = axes[idx]
#
#     # Calculate word frequencies per painting
#     painting_words = {}
#     for painting in paintings:
#         texts = df[df["Painting"] == painting][col].dropna()
#         words = []
#         for text in texts:
#             # Simple tokenization (match your convert_data.py approach)
#             import re
#             words.extend(re.split(r'\W+', str(text).lower()))
#         words = [w for w in words if len(w) > 2]  # Remove short words
#         painting_words[painting] = Counter(words)
#
#     # Calculate distinctiveness score for top words
#     all_words = set()
#     for counter in painting_words.values():
#         all_words.update(counter.keys())
#
#     distinctiveness = {}
#     for word in all_words:
#         scores = []
#         for painting in paintings:
#             freq = painting_words[painting].get(word, 0) + 1  # Laplace smoothing
#             scores.append(freq)
#         # Distinctiveness = max frequency / average frequency
#         distinctiveness[word] = max(scores) / (sum(scores) / len(scores))
#
#     # Get top 10 most distinctive words
#     top_words = sorted(distinctiveness.items(), key=lambda x: x[1], reverse=True)[:10]
#
#     # Create horizontal bar chart
#     words, scores = zip(*top_words)
#     y_pos = range(len(words))
#     bars = ax.barh(y_pos, scores, color=['#FF9999', '#99FF99', '#9999FF'][idx % 3])
#     ax.set_yticks(y_pos)
#     ax.set_yticklabels(words)
#     ax.set_xlabel("Distinctiveness Score", fontsize=10)
#     ax.set_title(f"{col[:50]}...", fontsize=10)
#     ax.axvline(x=2.0, color='red', linestyle='--', alpha=0.5, label='High distinctiveness threshold')
#
#     # Annotate which painting each word is most associated with
#     for i, word in enumerate(words):
#         max_painting = max(painting_words.keys(), key=lambda p: painting_words[p].get(word, 0))
#         bars[i].set_label(max_painting if i == 0 else "")
#
#     if idx == 0:
#         ax.legend(loc='lower right', fontsize=8)
#
# plt.tight_layout()
# plt.savefig('text_features_distinctiveness.png', dpi=150, bbox_inches='tight')
# plt.show()
#
# # Print summary for write-up
# print("\n=== Text Feature Distinctiveness Summary ===")
# for col in text_columns:
#     print(f"\n{col[:50]}...")
#     # Count words with high distinctiveness
#     texts = df[col].dropna()
#     all_text = ' '.join(texts.astype(str))
#     words = re.split(r'\W+', all_text.lower())
#     unique_words = set([w for w in words if len(w) > 2])
#     print(f"  Vocabulary size: {len(unique_words)}")
#
#
#
#
# # Figure 5: Heatmap showing strength of association for all feature types
# import seaborn as sns
#
# # Calculate association metrics for each feature
# results = []
#
# # 1. Numerical features (ANOVA F-statistic normalized)
# numerical_cols = [
#     "On a scale of 1–10, how intense is the emotion conveyed by the artwork?",
#     "How many prominent colours do you notice in this painting?",
#     "How many objects caught your eye in the painting?",
#     "How much (in Canadian dollars) would you be willing to pay for this painting?",
#     "This art piece makes me feel sombre.",
#     "This art piece makes me feel content.",
#     "This art piece makes me feel calm.",
#     "This art piece makes me feel uneasy."
# ]
#
# for col in numerical_cols:
#     groups = [df[df["Painting"] == p][col].dropna().values for p in paintings]
#     groups = [g for g in groups if len(g) > 0]
#     if len(groups) >= 2:
#         f_stat, p_val = stats.f_oneway(*groups)
#         # Normalize F-statistic to 0-1 range (cap at 100)
#         strength = min(f_stat / 100, 1.0)
#         results.append({"Feature": col[:40], "Type": "Numerical", "Strength": strength})
#
# # 2. Categorical features (Cramér's V)
# for col, title in categorical_features:
#     contingency = pd.crosstab(df["Painting"], df[col])
#     chi2, p, dof, expected = stats.chi2_contingency(contingency)
#     n = contingency.sum().sum()
#     cramers_v = np.sqrt(chi2 / (n * (min(contingency.shape) - 1)))
#     results.append({"Feature": title, "Type": "Categorical", "Strength": cramers_v})
#
# # 3. Text features (using mutual information approximation)
# for col in text_columns:
#     # Simplified: count of unique words as proxy for information content
#     unique_words_per_painting = []
#     for painting in paintings:
#         texts = df[df["Painting"] == painting][col].dropna()
#         all_words = ' '.join(texts.astype(str)).lower()
#         words = set(re.split(r'\W+', all_words))
#         unique_words_per_painting.append(len(words))
#
#     # Strength based on variation across classes
#     strength = np.std(unique_words_per_painting) / np.mean(unique_words_per_painting)
#     results.append({"Feature": col[:40], "Type": "Text", "Strength": min(strength, 1.0)})
#
# # Create heatmap
# df_results = pd.DataFrame(results)
# pivot = df_results.pivot(index="Feature", columns="Type", values="Strength").fillna(0)
#
# fig, ax = plt.subplots(figsize=(10, 8))
# sns.heatmap(pivot, annot=True, cmap='RdYlGn', vmin=0, vmax=1,
#             fmt='.2f', linewidths=0.5, ax=ax, cbar_kws={'label': 'Association Strength'})
# ax.set_title("Feature-Label Association Strength by Feature Type", fontsize=14)
# ax.set_xlabel("")
# plt.tight_layout()
# plt.savefig('feature_association_heatmap.png', dpi=150)
# plt.show()
