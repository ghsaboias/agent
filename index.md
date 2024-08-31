---
layout: default
title: MetaBlog
---

<h1>{{ page.title }}</h1>

<p>Welcome to my automatically generated blog about technology and innovation!</p>

<h2>Latest Post</h2>
{% for post in site.posts limit:1 %}
  <h3>
    <a href="{{ post.url | relative_url }}">
      {{ post.title }}
    </a>
  </h3>
  <p>{{ post.date | date: "%B %d, %Y" }}</p>
  <p>{{ post.excerpt }}</p>
{% endfor %}

<h2>All Posts</h2>
<ul>
  {% for post in site.posts %}
    <li>
      <h3>
        <a href="{{ post.url | relative_url }}">
          {{ post.title }}
        </a>
      </h3>
      <p>{{ post.date | date: "%B %d, %Y" }}</p>
    </li>
  {% endfor %}
</ul>

<p><a href="/feed.xml">Subscribe via RSS</a></p>