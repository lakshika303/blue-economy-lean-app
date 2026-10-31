# Blue Economy–Lean Decision Support Application

This is a simple Streamlit application that uses `Portal.xlsx` to display the relationships between:
- Impact
- Blue Economy practice
- Challenge
- Lean principle (`Lean P.`)

## Run locally
1. Install Python.
2. Open a terminal in this folder.
3. Install dependencies:
   `pip install -r requirements.txt`
4. Start the application:
   `streamlit run app.py`

## Deploy with GitHub and Streamlit Community Cloud
1. Create a GitHub repository.
2. Upload `app.py`, `requirements.txt`, and `Portal.xlsx` to the repository.
3. Open https://share.streamlit.io/ and sign in with GitHub.
4. Choose **Create app**, select your repository and branch, and set the main file path to `app.py`.
5. Deploy.

## Important
- `Portal.xlsx` must be in the same repository folder as `app.py`.
- The Excel file must contain columns named `Impact`, `Practice`, `Challenge`, and `Lean P.`. Extra spaces around column names are accepted.
- The current dataset uses coded labels (e.g. I1, P1, C1, L1). Replace them with descriptive labels in Excel if you want those names displayed in the application.
- Only include information you are comfortable making available through the deployed application. A public GitHub repository can expose its contents.
