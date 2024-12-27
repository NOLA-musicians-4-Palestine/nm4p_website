---
layout: band
---
## Upcoming Rehearsals:

- Thusday, 1/2, 7:30-9:30p
- Sunday, 1/5,2-4p.

Location: Architect Alley/Street

## Rep List
### Current Rep

{% for song in site.songs %}
{% if song.status == "current" %}
- [{{song.title}}]({{song.url}})
{% endif %}
{% endfor %}

### Songs we're currently learning
{% for song in site.songs %}
{% if song.status == "learning" %}
- [{{song.title}}]({{song.url}})
{% endif %}
{% endfor %}
 

### Songs we want to play
We don't have arrangements for these yet, but they're on our radar.
If you want to make an arrangement that'd be cool.

{% for song in site.songs %}
{% if song.status == "future" %}
- [{{song.title}}]({{song.url}})
{% endif %}
{% endfor %}

## Resources

[Chants with Arabic Rhythms](/chants_and_rhythms.html)

[Maqam World](https://maqamworld.com/)
