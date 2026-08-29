---
layout: band
---

## [We Released An Album!]({{"from_new_orleans_to_palestine.html" | relative_url}})

<h3>📥 <a href="{{ "/charts.html" | relative_url }}">Build your chart book</a></h3>
<p>Choose your part/transposition and download all your charts as a PDF.</p>

<div class="olive-pattern-bg">
    <h2>Rep List</h2>
</div>

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

<div class="olive-pattern-bg">
    <h2>Resources</h2>
</div>

- [Chants with Arabic Rhythms](chants_and_rhythms.html)
- [Maqam World](https://maqamworld.com/)


<div class="olive-pattern-bg">
    <h2>Upcoming Band Events</h2>
</div>

{% include band_events.html %}
