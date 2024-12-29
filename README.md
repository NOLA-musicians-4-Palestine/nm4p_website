---
layout: readme
---

# Deployment Setup Instructions

To deploy this site from the `live` branch using the [included action](.github/workflows/pages-deploy.yml), click the **Settings** tab and the **Pages** section (or [here](../../settings/pages)) and ensure the **Source** is set to "Github Actions"

> ** Developer Note: ** to support deployments on other domains such as forks, use relative URL's in template content.

# site structure and status

## Home

- [x] invite people to join
- [x] display the mission statement and members/endorsers/partners
(text is not final, I've gotta get what's been done on the doc)
- [x] photos of the band (being compiled)
- [x] look good

once the text and images are there I think we can publish it and make the other parts of the site "coming soon"

## Plug In!

### Events

The community calendar,I was thinking cards scrolling horizontally?
Flyers - forget supporting just text. you need a flyer.

#### Design

- [x] Horizontal Scrolling cards
- [x] flyer
- [x] formatted info on click
- [x] sort by date fuck ya it's automatic
- [ ] date-based navigation (for later in javascript)
- [ ] filter by event host (org/band...) ?
- [x] do not show past events
- [ ] make something to show for when there are no upcoming events

#### thoughts

thoughts on easily getting people's events listed here:
we could make an instagram account and follow only members
set notification settings to get emails when anyone posts
it'd be someone's job to check the email daily and post the new stuff on the site
maybe that could be automated?

Probably a better system would be to have an email go out to the contact we have on file for each org/band asking them to reply with their events and flyers

I made nolamusicians4Palestine@gmail.com and made this event submission form (for the free storage)
where people can upload their flyers and info

I'm hoping to automate the posting/reviewing process


### Updates from the Community

- [ ] regular blog where orgs can post updates
	- [x] posts datastructure
	- [x] layout for posts
	- [ ] display list an

#### design thoughts

the latest update from each org should be displayed (excerpt only)
click to see full update.

then a list of all posts

Each org should have a page that is their first post and then a list of their other posts

## Brass Band

- [x] Upcoming Rehearsals and Shows

### Rep List

- [x] Current rep
- [x] not started
- [x] learning

TODO: add lama bada?

### Song Pages

Each song should have a page with
 - [ ] reference recordings
 - [ ] rehearsal recordings
 - [ ] arrangement notes
 - [ ] charts/files
 - [ ] context

#### thoughts:
We should have naming convention for the chart files so that
jekyll can automatically understand what part key and clef it is
in order to make them available in the chart finder and the song pages.
maybe: 
```
Song_name-Part-Transposition-clef.pdf
```

I'm implementing songs as collections. so to add a song you add a md file to the \_songs folder with the appropriate metadata, content can be used for context and arrangement notes
I should make a custom layout (maybe child layout?) that has the different charts/files

### Chart Pages
	
- [ ] Chart
- [ ] Chart Finder at the top

Chart finder: 
song v part v transposition v clef v

### Chants

- [ ] chant list
- [ ] audio/video recording with a rhythm

## every page (in the footer)

- [x] contact and join email list on every page
- [ ] except the chart pages (half done, there's a chart layout now)



# website stuff

the git history is all fucked up. I only want to keep the live branch

[Photos from Fatima](https://www.icloud.com/sharedalbum/#B0hG4TcsmJ8ZSnK;D502F7AE-9C26-4CBF-B3C8-537F91F93CE0)
