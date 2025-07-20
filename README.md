# TuniCompare

TuniCompare is a lightweight product comparison platform built for educational purposes. It scrapes product data (Laptops, Desktops, and Screens) from leading Tunisian e-commerce websites — Mytek, Tunisianet, and ScoopGaming — and serves it through a minimal Flask backend with a clean HTML/CSS/JavaScript frontend. The site design is responsive, modern, and optimized for clarity and usability.

## Key Techniques

- **Scraping product data** using custom Python scripts, then exporting to structured `.csv` files grouped by category and source site. These files are then parsed and loaded into a PostgreSQL database for dynamic querying.

- **Custom fuzzy matching and specification comparison**: Implements a rule-based algorithm to match identical products listed across different sites by comparing normalized specs (e.g., CPU, RAM, GPU) and using fuzzy string matching for inconsistent naming.

- **Dynamic DOM rendering**: Uses `document.createElement()` and modular JavaScript to fetch and populate product cards from backend API responses. [MDN Reference](https://developer.mozilla.org/en-US/docs/Web/API/Document/createElement)

- **Modern and clean UI design**: Built using only HTML and CSS (no frameworks), featuring grid/flex layouts, component-based styling, and category-specific product views.

## Notable Technologies

- **Python** — Backend logic, scraping, data parsing
- **Flask** — Lightweight web framework used for routing and JSON APIs
- **PostgreSQL / SQLite3** — Relational database systems for persistent product storage
- **JavaScript (vanilla)** — Fetches and displays data dynamically
- **HTML / CSS** — Semantic markup and modern responsive design

## Project Structure

```
Main/
├── Products/
│   └── [CSV files scraped from each site by product type]
├── Resources/
│   └── [Logos, icons, product placeholder images]
├── Code/
│   ├── .venv/
│   ├── Backend/
│   │   ├── Scraping/
│   │   └── DB.py
│   ├── Website/
│   │   ├── Home/
│   │   └── Shop/
│   │       ├── Desktop/
│   │       ├── Laptop/
│   │       └── Screen/
```

### Directory Highlights

- **Products/** — Raw scraped data in CSV format, grouped by site and category
- **Resources/** — All logos and image assets used in the UI
- **Backend/** — Scraping logic and the `DB.py` module for parsing and inserting CSV content into PostgreSQL
- **Website/Shop/** — Contains separate folders per category with self-contained HTML, CSS, and JS for each

## Learned Skills

This project helped develop practical experience in:

- Designing and structuring a backend/frontend codebase
- Writing scraping scripts and handling real-world messy data
- Working with SQL-based databases and schema design
- Building lightweight APIs with Flask
- Creating reusable HTML/CSS layouts without relying on frameworks
- Parsing and matching inconsistent product data using fuzzy logic
- Serving dynamic content using vanilla JavaScript

## Disclaimer

This is a non-commercial, learning-focused project. All data is used strictly for educational purposes. The platform is not intended for public release, monetization, or competition with the original retailers.
