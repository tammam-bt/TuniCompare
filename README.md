# 🛒 TuniCompare

[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)](https://postgresql.org)
[![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)](https://developer.mozilla.org/en-US/docs/Web/JavaScript)
[![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white)](https://developer.mozilla.org/en-US/docs/Web/HTML)
[![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white)](https://developer.mozilla.org/en-US/docs/Web/CSS)

> 🎓 **Educational Project** | 📊 **Product Comparison Platform** | 🇹🇳 **Made in Tunisia**

TuniCompare is a lightweight product comparison platform built for educational purposes. It scrapes product data (💻 Laptops, 🖥️ Desktops, and 📺 Screens) from leading Tunisian e-commerce websites — **Mytek**, **Tunisianet**, and **ScoopGaming** — and serves it through a minimal Flask backend with a clean HTML/CSS/JavaScript frontend. The site design is responsive, modern, and optimized for clarity and usability.

## ✨ Key Features

- 🕷️ **Smart Web Scraping** — Custom Python scripts extract product data and export to structured `.csv` files grouped by category and source site. Data is then parsed and loaded into PostgreSQL for dynamic querying.

- 🔍 **Intelligent Product Matching** — Rule-based algorithm matches identical products across different sites by comparing normalized specs (CPU, RAM, GPU) using fuzzy string matching for inconsistent naming.

- ⚡ **Dynamic DOM Rendering** — Uses `document.createElement()` and modular JavaScript to fetch and populate product cards from backend API responses. [📖 MDN Reference](https://developer.mozilla.org/en-US/docs/Web/API/Document/createElement)

- 🎨 **Modern UI Design** — Built with pure HTML and CSS (no frameworks), featuring grid/flex layouts, component-based styling, and category-specific views.

## 🛠️ Tech Stack

| Technology | Purpose | Badge |
|------------|---------|-------|
| **Python** | Backend logic, scraping, data parsing | ![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white) |
| **Flask** | Lightweight web framework for routing and APIs | ![Flask](https://img.shields.io/badge/Flask-000000?style=flat-square&logo=flask&logoColor=white) |
| **PostgreSQL** | Relational database for persistent storage | ![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=flat-square&logo=postgresql&logoColor=white) |
| **SQLite3** | Alternative lightweight database option | ![SQLite](https://img.shields.io/badge/SQLite-07405E?style=flat-square&logo=sqlite&logoColor=white) |
| **JavaScript** | Dynamic frontend interactions | ![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=flat-square&logo=javascript&logoColor=black) |
| **HTML5/CSS3** | Semantic markup and responsive design | ![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=flat-square&logo=html5&logoColor=white) ![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=flat-square&logo=css3&logoColor=white) |

## 📁 Project Structure

```
📦 Main/
├── 📊 Products/
│   └── 📄 [CSV files scraped from each site by product type]
├── 🖼️ Resources/
│   └── 🎨 [Logos, icons, product placeholder images]
├── 💻 Code/
│   ├── 🐍 .venv/
│   ├── ⚙️ Backend/
│   │   ├── 🕷️ Scraping/
│   │   └── 🗃️ DB.py
│   └── 🌐 Website/
│       ├── 🏠 Home/
│       └── 🛍️ Shop/
│           ├── 🖥️ Desktop/
│           ├── 💻 Laptop/
│           └── 📺 Screen/
```

### 📂 Directory Highlights

| Directory | Description | Icon |
|-----------|-------------|------|
| **Products/** | Raw scraped data in CSV format, grouped by site and category | 📊 |
| **Resources/** | All logos and image assets used in the UI | 🖼️ |
| **Backend/** | Scraping logic and `DB.py` module for PostgreSQL integration | ⚙️ |
| **Website/Shop/** | Category-specific folders with self-contained HTML, CSS, and JS | 🛍️ |

## 🚀 Skills Developed

This project provided hands-on experience with:

- 🏗️ **Full-Stack Development** — Designing and structuring backend/frontend architecture
- 🕷️ **Web Scraping** — Writing robust scripts and handling real-world messy data
- 🗃️ **Database Management** — Working with SQL databases and schema design
- 🌐 **API Development** — Building lightweight REST APIs with Flask
- 🎨 **Frontend Design** — Creating responsive layouts without frameworks
- 🔍 **Data Processing** — Implementing fuzzy logic for inconsistent product matching
- ⚡ **Dynamic Content** — Serving real-time data using vanilla JavaScript

## ⚠️ Educational Disclaimer

> 🎓 **Learning Project Notice**
> 
> This is a **non-commercial, educational-focused project**. All data is used strictly for learning purposes. The platform is **not intended** for:
> - 💰 Public release or monetization
> - 🏢 Commercial competition with original retailers
> - 📈 Profit generation of any kind
>
> Built with ❤️ for educational exploration and skill development.
