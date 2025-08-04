# 🛒 TuniCompare

[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)](https://postgresql.org)
[![CSV](https://img.shields.io/badge/CSV-217346?style=for-the-badge&logo=microsoftexcel&logoColor=white)](https://en.wikipedia.org/wiki/Comma-separated_values)
[![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)](https://developer.mozilla.org/en-US/docs/Web/JavaScript)
[![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white)](https://developer.mozilla.org/en-US/docs/Web/HTML)
[![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white)](https://developer.mozilla.org/en-US/docs/Web/CSS)

> 🎓 **Educational Project** | 📊 **Product Comparison Platform** | 🇹🇳 **Made in Tunisia**

TuniCompare is a lightweight product comparison platform built for educational purposes. It scrapes product data (💻 Laptops, 🖥️ Desktops, and 📺 Screens) from leading Tunisian e-commerce websites — **Mytek**, **Tunisianet**, and **ScoopGaming** — and serves it through a minimal Flask backend with a clean HTML/CSS/JavaScript frontend. The site design is responsive, modern, and optimized for clarity and usability.

## ✨ Key Features

- 🕷️ **Smart Web Scraping** — Custom Python scripts extract product data and export to structured .csv files grouped by category and source site. Data is then parsed and loaded into PostgreSQL for dynamic querying.

- 🔧 **Intelligent Specs Extraction & Normalization** — Advanced parsing algorithms extract and standardize product specifications (CPU models, RAM capacity, GPU variants, storage types) from inconsistent raw data, enabling lightning-fast database queries and accurate comparisons.

- 🧠 **Complex Product Matching Algorithm** — Sophisticated multi-layer comparison system combining fuzzy string matching with deep specs analysis. The algorithm handles manufacturer naming inconsistencies, model variations, and specification formatting differences to accurately identify identical products across different retailers.

- 🔄 **Dynamic Product Loading on Scroll** — Seamless infinite scroll implementation that dynamically fetches and renders product batches as users browse, providing smooth performance even with large product catalogs while reducing initial page load times.

- 🎨 **Modern UI Design** — Built with pure HTML and CSS (no frameworks), featuring grid/flex layouts, component-based styling, and category-specific views.

- 💰 **Best Price Detection** — Intelligent price comparison system that automatically identifies and highlights the retailer offering the lowest price for each product, complete with visual indicators and savings calculations.

## 🛠️ Tech Stack

| Technology | Purpose | Badge |
|------------|---------|-------|
| **Python** | Backend logic, scraping, data parsing | ![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white) |
| **Flask** | Lightweight web framework for routing and APIs | ![Flask](https://img.shields.io/badge/Flask-000000?style=flat-square&logo=flask&logoColor=white) |
| **PostgreSQL** | Relational database for persistent storage | ![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=flat-square&logo=postgresql&logoColor=white) |
| **CSV** | Data storage and interchange format | ![CSV](https://img.shields.io/badge/CSV-217346?style=flat-square&logo=microsoftexcel&logoColor=white) |
| **Render** | Cloud platform for hosting and deployment | ![Render](https://img.shields.io/badge/Render-46E3B7?style=flat-square&logo=render&logoColor=white) |
| **JavaScript** | Dynamic frontend interactions | ![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=flat-square&logo=javascript&logoColor=black) |
| **HTML5/CSS3** | Semantic markup and responsive design | ![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=flat-square&logo=html5&logoColor=white) ![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=flat-square&logo=css3&logoColor=white) |

## 🌟 Try It Out!

Ready to explore TuniCompare? You have two options to experience the platform:

### 🚀 Option 1: Live Demo (Recommended)
**Experience TuniCompare instantly — no setup required!**

[![Visit TuniCompare](https://img.shields.io/badge/🌐_Visit_Live_Demo-4CAF50?style=for-the-badge&logoColor=white)](https://tunicompare.onrender.com/)

**👆 Click above or visit:** `https://tunicompare.onrender.com/`

✨ **Why try the live demo?**
- 🎯 **Instant Access** — See the platform in action immediately
- 📱 **Fully Responsive** — Test on any device (mobile, tablet, desktop)
- 🔄 **Real-Time Data** — Browse actual scraped product comparisons
- 🎨 **Complete Experience** — All features and UI components available

---

### 🔧 Option 2: Run Locally
**Perfect for developers who want to explore the code!**

#### Prerequisites
- Python 3.7 or higher
- Git

#### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/tunicompare.git
   cd tunicompare
   ```

2. **Set up PostgreSQL database**
   
   **Option A: Local PostgreSQL Installation**
   ```bash
   # Install PostgreSQL (Ubuntu/Debian)
   sudo apt update
   sudo apt install postgresql postgresql-contrib
   
   # Start PostgreSQL service
   sudo systemctl start postgresql
   sudo systemctl enable postgresql
   
   # Create database and user
   sudo -u postgres psql
   ```
   ```sql
   -- Inside PostgreSQL prompt
   CREATE DATABASE tunicompare_db;
   CREATE USER tunicompare_user WITH PASSWORD 'your_secure_password';
   GRANT ALL PRIVILEGES ON DATABASE tunicompare_db TO tunicompare_user;
   \q
   ```
   
   **Option B: Using Docker (Recommended for development)**
   ```bash
   # Pull and run PostgreSQL container
   docker run --name tunicompare-postgres \
     -e POSTGRES_DB=tunicompare_db \
     -e POSTGRES_USER=tunicompare_user \
     -e POSTGRES_PASSWORD=your_secure_password \
     -p 5432:5432 \
     -d postgres:13
   ```

3. **Create environment file**
   ```bash
   # Create a .env file in the project root
   touch .env
   ```
   Add your database credentials to the `.env` file:
   ```bash
   # Database connection details
   dbhost = localhost
   dbport = 5432
   dbname = tunicompare_db
   dbuser = tunicompare_user
   dbpass = your_secure_password
   dburl = postgresql://tunicompare_user:your_secure_password@localhost:5432/tunicompare_db
   ``` 

4. **Install dependencies**
   ```bash
   # Create virtual environment (recommended)
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   
   # Install required Python packages
   pip install -r requirements.txt
   ```

5. **Initialize database and scrape data**
   ```bash
   # Run the scraping pipeline to populate database
   python run.py
   ```

6. **Start the Flask application**
   ```bash
   # Run the main application
   python app.py
   ```

7. **Access locally**
   Open your browser and navigate to `http://localhost:5000`

The website will now be running on your local server with a fully populated database! 🎉

---

> 💡 **Pro Tip**: Start with the [live demo](https://tunicompare.onrender.com/) to get a feel for the platform, then set it up locally if you want to dive into the code and contribute!

## 📁 Project Structure

```
📦 TuniCompare/
├── 🚀 app.py                          # Main Flask application & routing
├── 🔄 run.py                          # Data scraping & database population
├── 📋 requirements.txt                # Python dependencies
├── 🐍 .venv/                          # Virtual environment
│
├── 📊 Main/
│   └── Products/                      # Raw scraped data storage
│       ├── 💻 laptops_mytek.csv
│       ├── 🖥️ desktops_tunisianet.csv
│       ├── 📺 screens_scoopgaming.csv
│       └── 📄 [Additional CSV files by category & site]
│
├── ⚙️ Scripts/                        # Backend processing modules
│   ├── 🕷️ scrapers/
│   │   ├── mytek_scraper.py
│   │   ├── tunisianet_scraper.py
│   │   └── scoopgaming_scraper.py
│   ├── 🔍 product_matcher.py          # Fuzzy matching algorithms
│   ├── 🗃️ database_manager.py         # PostgreSQL operations
│   └── 🔧 data_normalizer.py          # Specs extraction & standardization
│
├── 🎨 static/                         # Frontend assets
│   ├── CSS/
│   │   ├── 🎭 main.css               # Global styles
│   │   ├── 🏠 home.css               # Homepage specific
│   │   └── 🛍️ shop.css               # Product pages styling
│   ├── JS/
│   │   ├── ⚡ product_loader.js       # Dynamic scroll & API calls
│   │   ├── 🔍 search_filter.js       # Search & filtering logic
│   │   └── 💰 price_comparison.js     # Best price highlighting
│   └── Resources/
│       ├── 🖼️ logos/                  # Site & brand logos
│       ├── 📱 icons/                  # UI icons & graphics
│       └── 🎯 placeholders/           # Default product images
│
└── 📄 templates/                      # Jinja2 HTML templates
    ├── 🧩 base.html                   # Base template with common layout
    ├── 🏠 home.html                   # Landing page template
    └── 🛍️ shop/
        ├── 💻 laptop.html             # Laptop category page
        ├── 🖥️ desktop.html            # Desktop category page
        └── 📺 screen.html             # Screen category page
```

### 📂 Directory Breakdown

| **Component** | **Purpose** | **Key Files** |
|---------------|-------------|---------------|
| **🚀 Core Application** | Main Flask app and execution | `app.py` (routes & API), `run.py` (scraping pipeline) |
| **📊 Data Storage** | Raw CSV files organized by retailer and category | `Main/Products/*.csv` |
| **⚙️ Processing Scripts** | Backend logic for scraping, matching, and DB operations | `Scripts/scrapers/`, `product_matcher.py`, `database_manager.py` |
| **🎨 Frontend Assets** | Stylesheets, JavaScript, and media resources | `static/CSS/`, `static/JS/`, `static/Resources/` |
| **📄 Templates** | Jinja2 HTML templates with inheritance structure | `templates/base.html`, category-specific pages |

### 🔄 Workflow Overview

1. **`run.py`** → Executes scrapers → Normalizes data → Populates database
2. **`app.py`** → Serves templates → Provides API endpoints → Handles routing  
3. **Frontend JS** → Fetches data dynamically → Implements infinite scroll → Updates UI
4. **Templates** → Inherit from `base.html` → Category-specific layouts → Responsive design

## 🚀 Skills Developed

This project provided hands-on experience with:

- 🏗️ **Full-Stack Development** — Designing and structuring backend/frontend architecture
- 🕷️ **Web Scraping** — Writing robust scripts and handling real-world messy data
- 🗃️ **Database Management** — Working with SQL databases and schema design
- 🌐 **API Development** — Building lightweight REST APIs with Flask
- 🎨 **Frontend Design** — Creating responsive layouts without frameworks
- 🔍 **Data Processing** — Implementing fuzzy logic for inconsistent product matching
- ⚡ **Dynamic Scroll Loading** — Building infinite scroll pagination with JavaScript for optimal performance
- 🚀 **Cloud Deployment** — Deploying web applications and databases to production on Render platform

## 🤝 Support & Contribution

We'd love to hear from you! TuniCompare is an open educational project, and community interaction helps make it better.

### 🌟 Ways to Get Involved

- **⭐ Star this repository** if you find it useful or interesting
- **🐛 Report bugs** by opening an issue on GitHub
- **💡 Suggest features** or improvements through discussions
- **🔀 Submit pull requests** to contribute code improvements
- **📖 Share your experience** - let us know how you used this project for learning
- **🗣️ Spread the word** - share with fellow developers and students

### 📬 Get in Touch

- **GitHub Issues**: For bug reports and feature requests
- **Discussions**: For questions, ideas, and general conversation about the project
- **Educational Use**: If you're using this project for teaching or learning, we'd love to hear about your experience!

Your feedback and contributions help make TuniCompare a better learning resource for everyone. Every interaction, no matter how small, is appreciated! 🙏

## ⚠️ Educational Disclaimer

> 🎓 **Learning Project Notice**
> 
> This is a **non-commercial, educational-focused project**. All data is used strictly for learning purposes. The platform is **not intended** for:
> - 💰 Public release or monetization
> - 🏢 Commercial competition with original retailers
> - 📈 Profit generation of any kind
>
> Built with ❤️ for educational exploration and skill development.

---

## 🙏 Special Thanks

This project wouldn't have been possible without the incredible work of the technology teams behind the tools we use:

**🐍 Python Software Foundation** — For creating the versatile Python language that powers our backend logic and scraping capabilities.

**🌶️ Pallets Team** — For Flask, the elegant microframework that makes web development in Python a joy.

**🐘 PostgreSQL Global Development Group** — For the robust, reliable database system that handles our product data with precision.

**🚀 Render Team** — For providing an intuitive cloud platform that makes deployment accessible to developers everywhere.

**🌐 Mozilla Foundation & Web Standards Community** — For continuously pushing web technologies forward and maintaining comprehensive documentation.

**🛍️ Mytek, Tunisianet & ScoopGaming** — The Tunisian e-commerce pioneers whose platforms inspire and enable educational projects like this one.

**🇹🇳 Tunisian Tech Community** — For fostering innovation and supporting educational development in our region.

Every line of code, every database query, and every user interaction stands on the shoulders of these incredible teams and communities. Thank you for making technology accessible and empowering the next generation of developers! 🚀
