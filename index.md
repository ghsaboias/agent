   ---
   layout: home
   title: MetaBlog
   ---

   Welcome to my automatically generated blog about technology and innovation!

   {% for post in site.posts %}
     <h2><a href="{{ post.url }}">{{ post.title }}</a></h2>
     <p>{{ post.date | date_to_string }}</p>
     <p>{{ post.excerpt }}</p>
   {% endfor %}