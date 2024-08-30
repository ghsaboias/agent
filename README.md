# Automated AI Blog Post Generator

This project uses AI to automatically generate and publish blog posts about technology and innovation. It leverages the Groq API for content generation and GitHub Actions for automation.

## Features

- Automated topic generation
- AI-powered content research and writing
- Dynamic category extraction
- Automated publishing to a GitHub Pages blog
- Scheduled runs via GitHub Actions

## Setup

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/your-repo-name.git
   cd your-repo-name
   ```

2. Install the required Python packages:
   ```
   pip install -r requirements.txt
   ```

3. Set up your Groq API key:
   - Go to your GitHub repository settings
   - Navigate to Secrets and Variables > Actions
   - Add a new repository secret named `GROQ_API_KEY` with your Groq API key as the value

4. Configure GitHub Pages:
   - Go to your repository settings
   - Navigate to Pages
   - Set the source to GitHub Actions

## Usage

The blog post generation process is automated via GitHub Actions. By default, it runs every 3 minutes for testing purposes and stops after 3 iterations.

To manually trigger the workflow:
1. Go to the Actions tab in your GitHub repository
2. Select the "Generate Blog Post" workflow
3. Click "Run workflow"

Generated blog posts will appear in the `posts/` directory.

## Customization

- Adjust the scheduling in `.github/workflows/generate_blog_post.yml`
- Modify the content generation prompts in `main.py`
- Customize the blog post format and categories in the `save_blog_post` function

## Files

- `main.py`: Main script for blog post generation
- `requirements.txt`: Required Python packages
- `.github/workflows/generate_blog_post.yml`: GitHub Actions workflow
- `posts/`: Directory containing generated blog posts

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available under the [MIT License](LICENSE).