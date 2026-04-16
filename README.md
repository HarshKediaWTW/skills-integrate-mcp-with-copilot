# Integrate MCP with Copilot

<img src="https://octodex.github.com/images/Professortocat_v2.png" align="right" height="200px" />

Hey HarshKediaWTW!

Mona here. I'm done preparing your exercise. Hope you enjoy! 💚

Remember, it's self-paced so feel free to take a break! ☕️

[![](https://img.shields.io/badge/Go%20to%20Exercise-%E2%86%92-1f883d?style=for-the-badge&logo=github&labelColor=197935)](https://github.com/HarshKediaWTW/skills-integrate-mcp-with-copilot/issues/1)

## Local development

1. Install dependencies:

	```bash
	pip install -r requirements.txt
	```

2. Start the app:

	```bash
	uvicorn src.app:app --reload
	```

3. Open http://127.0.0.1:8000/static/index.html in your browser.

The backend now persists activities and registrations in a local SQLite database at `src/data/activities.db`.
On first run, the database is created automatically and seeded from `src/data/activities_seed.json`.

---

&copy; 2025 GitHub &bull; [Code of Conduct](https://www.contributor-covenant.org/version/2/1/code_of_conduct/code_of_conduct.md) &bull; [MIT License](https://gh.io/mit)

