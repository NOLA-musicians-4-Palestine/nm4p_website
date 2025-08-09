---
layout: readme
---

# Development Notes

## setup environment

TODO: write down how to install the necessary components, like podman, ruby and jekyll (maybe I could containerize those...)

## Pull Events from Google Calendar

```bash
podman run --rm \
  -w /workspace \
  -v [your path here]/nm4p_website:/workspace:z \
  localhost/nm4p-tools:latest \
  python tools/sync_calendars.py
```

## serve the site locally

```bash
bundle exec jekyll serve --livereload
```

## site structure

(what goes where...) TODO

# Deployment Setup Instructions

To deploy this site from the `live` branch using the [included action](.github/workflows/pages-deploy.yml), click the **Settings** tab and the **Pages** section (or [here](../../settings/pages)) and ensure the **Source** is set to "Github Actions"

> ** Developer Note: ** to support deployments on other domains such as forks, use relative URL's in template content.


# Website Wishlist

- [ ] know who's QR codes were scanned
    - xmlhttp request to submit a google form
- [ ] Generate QR codes with a runner that fetches files from google drive
    - [ ] make the qr code unique to each band
- [ ] more photos
- [ ] date-based navigation, filters
- [ ] handle old events better
- [ ] download events in batches of 10 dynamically
    - the pages are pre-rendered by jekyll, just not served
- [ ] make something to show for when there are no upcoming events
- [ ] automate followup email
- [ ] regular blog where orgs can post updates
- [ ] content pulled from google docs
    - song contexts
- [ ] files populated from google drive
- [ ] Upcoming Rehearsals and Shows from a google sheet
- [ ] chant list
- [ ] make sure everything that needs to be environment variables are that way
    - [ ] document how to clone the repository and make your own
