# ScreenshotSite
Gather screenshots of a site using your local chrome browser.

## To run

You need python, and you need the dependancies installed. This project uses `uv` for that task, found here: https://docs.astral.sh/uv/getting-started/installation/ 

After installing uv

    uv venv .venv
    uv sync
    source .venv/bin/activate
    python sssite.py example.com https://websiteurl.example.com

Captures all inks from the URL that are within the domain, and saves the pages as images in the screenshots directory.


## Credits

This is free to use, I got most of this code from the selenium example on their site, gettting started. 

