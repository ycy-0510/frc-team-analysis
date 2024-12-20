# Team Analysis

This project fetches and analyzes data for various FRC teams, including their awards and other relevant information.
![Screenshot of Team Analysis](https://cloud-2kwd61dsi-hack-club-bot.vercel.app/0screen_shot_2024-12-20_at_12.49.51___am.png)


![Screenshot of Team Analysis Data](https://cloud-2kwd61dsi-hack-club-bot.vercel.app/1screen_shot_2024-12-20_at_12.49.26___am.png)


## Prerequisites

- Python 3.x
- `pip` (Python package installer)
- WebDriver for Safari (or another browser of your choice)

## Installation

1. Clone the repository:

   ```sh
   git clone https://github.com/yourusername/teamanalysis.git
   cd teamanalysis
   ```
2. Install the required Python packages:

   ```sh
   pip install -r requirements.txt
   ```
> Note: When using Homebrew on macOS, it is recommended to use a virtual environment (venv).
3. Create a `.env` file in the root directory and add your TBA API key:

   ```env
   API_KEY=your_api_key_here
   ```

## Usage

1. Run the script:

   ```sh
   python main.py
   ```
2. The script will fetch data for the specified teams and save the results in an Excel file named `output/team_awards_{year}_{event}.xlsx`.

## Configuration

- You can modify the list of team numbers in `main.py` to fetch data for different teams.
- Ensure the WebDriver is correctly set up for your browser.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgements

- [The Blue Alliance API](https://www.thebluealliance.com/apidocs/v3) for providing the data.
- [pandas](https://pandas.pydata.org/) for data manipulation.
- [Selenium](https://www.selenium.dev/) for web scraping.
