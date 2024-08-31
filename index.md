   ---
   layout: home
   title: MetaBlog
   ---

   Welcome to my automatically generated blog about technology and innovation!

   {% for post in site.posts %}
     <h2>
       <a href="{{ post.url | relative_url }}">
         {{ post.title }}
       </a>
     </h2>
     <p>{{ post.date | date: "%B %d, %Y" }}</p>
     {% if post.excerpt %}
       {{ post.excerpt }}
     {% endif %}
   {% endfor %}