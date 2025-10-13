---
layout: band
---
<h2>
    Want us to play at an event? Fill out
    <a href="https://docs.google.com/forms/d/e/1FAIpQLSdEZuyxhZAG2gfDAK0pyeh1jTGqRGyUqhmNtO_spFiCFWX1JA/viewform?usp=header" target="_blank">this form!</a>
</h2>

## Upcoming Events:

{% include hanoun-events.md %}

## Rep List
### Current Rep

{% for song in site.songs %}
{% if song.status == "current" %}
- [{{song.title}}]({{song.url | relative_url}})
{% endif %}
{% endfor %}

### Songs we're currently learning
{% for song in site.songs %}
{% if song.status == "learning" %}
- [{{song.title}}]({{song.url | relative_url}})
{% endif %}
{% endfor %}
 

### Songs we want to play
We don't have arrangements for these yet, but they're on our radar.
If you want to make an arrangement that'd be cool.

{% for song in site.songs %}
{% if song.status == "future" %}
- [{{song.title}}]({{song.url | relative_url}})
{% endif %}
{% endfor %}

## Resources

[Chants with Arabic Rhythms](chants_and_rhythms.html)

[Maqam World](https://maqamworld.com/)
