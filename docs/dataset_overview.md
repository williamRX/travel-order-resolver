# Dataset Design Overview — First Findings

## 🎯 Goal of the Dataset

The objective is to build a comprehensive dataset that enables a machine learning model to classify user sentences into three distinct categories:

- **VALID** → Explicit request for an itinerary or route between two places
- **INVALID** → Sentences not related to itinerary requests
- **AMBIGU** → Sentences about places or movements but not explicitly requesting an itinerary

This dataset will serve as a critical security layer in the pipeline by filtering irrelevant inputs before they reach the core itinerary processing system. By accurately classifying user inputs, we can ensure that only valid route requests are processed, improving system efficiency and user experience.

---

## 🧩 Definitions & Examples

### 1. VALID Sentences

**Definition:** Sentences that explicitly request an itinerary or route between two distinct locations.

**Key Characteristics:**
- Clear origin and destination
- Explicit travel intent
- Request for route information, distance, or travel time

**Examples:**
- "Combien de temps pour aller de Lyon à Marseille ?"
- "Donne-moi la distance entre Paris et Roubaix."
- "Je veux un trajet de Bordeaux vers Toulouse."
- "Comment me rendre à Nice depuis Marseille ?"
- "trajet paris lille svp"
- "jveux aller de nantes a rennes"

**Expected Diversity:**
- **SMS language:** Abbreviations, informal expressions ("jveux", "chui", "stp")
- **Spelling errors:** Common typos in city names ("pariis", "toulousse", "bordo")
- **Short forms:** Minimal phrases ("paris lyon", "dep marseille dest nice")
- **Polite / familiar:** Various levels of formality ("peux-tu", "donne-moi", "je veux")
- **Multiple formulations:** Different grammatical structures and word orders
- **Mixed languages:** Occasional code-switching
- **Emojis:** Visual elements (🚆, 🎫, 📍)
- **Punctuation variations:** Missing or incorrect punctuation

### 2. INVALID Sentences

**Definition:** Sentences that do not request an itinerary, regardless of whether they mention cities or travel-related terms.

**Key Characteristics:**
- No clear origin-destination relationship
- No explicit itinerary request
- Irrelevant to route planning

**Examples:**
- "Paris est magnifique la nuit."
- "Peux-tu m'aider à cuisiner du riz ?"
- "J'ai perdu mon billet de train."
- "Je suis à Lyon."
- "Quel temps fait-il à Marseille ?"
- "J'aime les trains."

**Expected Diversity:**
- **Irrelevant topics:** General conversation, questions about cities, unrelated requests
- **Random conversations:** Casual chat, greetings, random statements
- **Sentences mentioning cities without itinerary request:** City descriptions, weather queries, general information
- **Noisy phrases:** Random characters, typos, absurd text ("asdadadasd", "mdrrr t ki")
- **Truncated phrases:** Incomplete sentences ("je veux", "aller", "train")
- **Wrong structure:** Sentences with cities but no valid origin-destination relationship

### 3. AMBIGU Sentences

**Definition:** Sentences that refer to cities or movement but lack a clear, explicit intention to request an itinerary.

**Key Characteristics:**
- Mention of locations or travel
- Unclear intent (could be a statement, question, or partial request)
- Requires context or clarification

**Examples:**
- "Je vais bientôt partir à Paris rejoindre ma mère qui arrive de Toulouse."
- "Je viens d'arriver à Marseille depuis Bordeaux."
- "Je dois aller à Lyon demain."
- "Je pars de Nice."
- "Direction Paris ?"
- "Je veux voyager mais je ne sais pas où."

**Why Ambiguity Matters:**
- **Improves robustness:** Helps the model handle edge cases and real-world complexity
- **Real-world relevance:** Users often write ambiguous messages that need clarification
- **Better user experience:** Allows the system to ask for clarification rather than failing silently
- **Prevents false positives:** Reduces the risk of misclassifying statements as requests

---

## 📏 Recommended Data Distribution

### Optimal Split

Based on real-world usage patterns and model training best practices, the recommended distribution is:

- **INVALID:** ~70%
- **VALID:** ~20–25%
- **AMBIGU:** ~5–10%

### Rationale

**Why INVALID is the majority:**
- **Prevents over-prediction:** Most text in real-world scenarios is not a route request. Training with a majority of INVALID examples prevents the model from over-predicting VALID.
- **Matches real-world distribution:** In production, the majority of user inputs will be irrelevant to itinerary requests.
- **Improves precision:** A model trained with more negative examples will have better precision for VALID predictions.
- **Reduces false positives:** Critical for a security/filtering layer where false positives can degrade user experience.

**Why VALID is 20–25%:**
- Sufficient examples to learn the various patterns of valid requests
- Balances recall (finding all valid requests) with precision (not misclassifying invalid as valid)

**Why AMBIGU is 5–10%:**
- Represents a smaller but important edge case
- Enough examples to learn the pattern without overwhelming the model
- Allows the system to handle ambiguous cases gracefully

---

## 🧪 Handling Ambiguity

### Approach 1: 3-Class Classification

**Description:** Train a single model with three output classes: VALID, INVALID, AMBIGU.

**Pros:**
- Single model to maintain
- Direct classification into all three categories
- Simpler deployment pipeline

**Cons:**
- More complex training (imbalanced classes)
- Requires careful handling of the AMBIGU class
- May need more data for the minority class

### Approach 2: 2-Class Classifier + Confidence Threshold

**Description:** Train a binary classifier (VALID vs. INVALID) and use confidence scores to determine ambiguity.

**Decision Logic:**
- **High confidence VALID** → VALID
- **High confidence INVALID** → INVALID
- **Low confidence (middle zone)** → AMBIGU

**Pros:**
- Simpler binary classification problem
- Confidence scores provide interpretability
- Flexible threshold tuning
- Can adjust ambiguity zone based on requirements

**Cons:**
- Requires threshold calibration
- Two-stage decision process
- May need separate confidence calibration

**Recommendation:** Start with Approach 2 (2-class + threshold) for easier initial development, then consider Approach 1 if ambiguity handling becomes critical.

---

## 📚 Dataset Requirements

To build a robust, production-ready dataset, the following requirements must be met:

### Scale
- **At least 50k–100k sentences** to ensure sufficient diversity and coverage
- Larger datasets (100k+) preferred for transformer-based models

### Diversity
- **Massive diversity** in sentence structures, lengths, and formulations
- **Realistic user-like phrasing** that mimics actual user behavior
- **Typos and spelling errors** common in real-world inputs
- **Slang and informal language** (SMS style, abbreviations)
- **Mixed languages** when relevant to the use case
- **Different levels of clarity** from very explicit to highly ambiguous

### Geographic Coverage
- **City names from multiple countries** (France, Belgium, Switzerland, Luxembourg, etc.)
- **Various city name formats** (with/without hyphens, accents, abbreviations)
- **Common misspellings** of city names

### Noise and Edge Cases
- **Random noise** and expressions
- **Truncated phrases** and incomplete sentences
- **Absurd text** and nonsensical inputs
- **Emojis and special characters**
- **Punctuation variations** (missing, incorrect, excessive)

### Quality Assurance
- **No duplicate sentences** (or minimal duplicates)
- **Balanced representation** across all categories
- **Validation** of examples to ensure correct labeling
- **Regular updates** to incorporate new patterns and edge cases

---

## 🛠️ Next Steps

### Pipeline Development

1. **Build a Baseline Model**
   - Start with simple models (Logistic Regression, SVM)
   - Establish performance benchmarks
   - Identify key features and patterns

2. **Measure Performance**
   - Define evaluation metrics (precision, recall, F1-score)
   - Create validation and test sets
   - Monitor performance across all three classes

3. **Train with Larger Datasets**
   - Scale up to 50k+ sentences
   - Experiment with data augmentation
   - Fine-tune class distributions

4. **Improve Model with Transformers**
   - Experiment with pre-trained French language models (CamemBERT, FlauBERT)
   - Fine-tune for the specific classification task
   - Optimize for production deployment

5. **Deploy with Threshold-Based Decision System**
   - Implement confidence-based ambiguity detection
   - Set up monitoring and logging
   - Create feedback loops for continuous improvement

### Continuous Improvement
- **Collect real-world examples** from production
- **Regular dataset updates** with new patterns
- **A/B testing** of different model versions
- **User feedback integration** to refine classifications

---

## 📊 Dataset Statistics (Target)

| Category | Count | Percentage |
|----------|-------|------------|
| INVALID  | 35,000 | 70%        |
| VALID    | 12,500 | 25%        |
| AMBIGU   | 2,500  | 5%         |
| **Total** | **50,000** | **100%** |

*Note: These numbers are targets for initial dataset. Scale up as needed.*

---

## 🎉 Conclusion

This dataset serves as the foundation for a robust classification system that will filter and route user inputs appropriately. By carefully designing the dataset with proper distribution, diversity, and ambiguity handling, we can build a model that performs well in production and provides a secure, efficient pipeline for itinerary processing.

The key to success lies in:
- **Diversity** to handle real-world variability
- **Balance** to prevent model bias
- **Quality** to ensure accurate classifications
- **Scale** to support robust model training

