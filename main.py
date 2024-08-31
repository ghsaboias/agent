import os
import logging
import time
import re
from datetime import datetime
from groq import Groq
from colorama import Fore, Style, init
from sklearn.feature_extraction.text import TfidfVectorizer

# Initialize colorama
init(autoreset=True)

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Disable debug logging for the 'httpx' library (used by Groq)
logging.getLogger('httpx').setLevel(logging.WARNING)

# Initialize Groq client
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def generate_response(messages, role):
    """Generate a response using the Groq API."""
    try:
        logger.debug(f"Generating response for {role}")
        start_time = time.time()
        chat_completion = client.chat.completions.create(
            messages=messages,
            model="llama3-8b-8192",
            max_tokens=1000,
            temperature=0.7,
        )
        end_time = time.time()
        response = chat_completion.choices[0].message.content
        logger.debug(f"Response generated for {role} in {end_time - start_time:.2f} seconds")
        return response, end_time - start_time
    except Exception as e:
        logger.error(f"Error generating {role} response: {e}")
        return None, 0

def generate_topic(max_iterations=2):
    """Generate a topic using three creative agents."""
    messages = [
        {"role": "system", "content": f"You are three creative AI agents collaborating to generate an interesting and unique blog post topic about technology, innovation, or futurism. You have {max_iterations} rounds to refine and improve the topic. Be specific and aim for a topic that allows for in-depth exploration."},
        {"role": "user", "content": "Let's brainstorm an interesting topic for a blog post about technology, innovation, or futurism. Suggest a broad area or theme to start with."}
    ]
    
    for i in range(max_iterations):
        for agent in range(1, 4):
            prompt = f"Agent {agent}, consider the previous suggestions and propose a refined or new topic idea. Be creative and specific. This is round {i+1} of {max_iterations}."
            response, _ = generate_response(messages + [{"role": "user", "content": prompt}], f"Creative Agent {agent}")
            
            if response:
                print(f"{Fore.MAGENTA}Creative Agent {agent}: {response}{Style.RESET_ALL}\n")
                messages.append({"role": "assistant", "content": response})
            else:
                logger.warning(f"Failed to generate response for Creative Agent {agent}. Continuing with next agent.")
            
            time.sleep(1)  # Short delay between agents
    
    # Final topic selection
    final_prompt = "Based on our brainstorming session, what's the most interesting and specific topic we've come up with for the blog post? Provide a concise topic statement and a brief outline of key points to cover."
    final_topic, _ = generate_response(messages + [{"role": "user", "content": final_prompt}], "Topic Selector")
    
    return final_topic.strip() if final_topic else "The impact of technology on modern society"

def generate_citations(research_content):
    """Extract potential citations from research content."""
    citations = re.findall(r'\b(?:According to|As stated by|In the words of)\s+([^,\.]+)', research_content)
    formatted_citations = [f"- {citation}" for citation in set(citations)]
    return "\n".join(formatted_citations)

def extract_keywords(content, num_keywords=5):
    """Extract key topics from the content for SEO optimization."""
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform([content])
    feature_names = vectorizer.get_feature_names_out()
    sorted_items = sorted(zip(tfidf_matrix.tocsc().data, feature_names), key=lambda x: x[0], reverse=True)
    keywords = [item[1] for item in sorted_items[:num_keywords]]
    return keywords

def content_researcher(topic):
    """Research agent to gather relevant information on the topic."""
    research_prompt = [
        {"role": "system", "content": "You are an expert researcher specializing in technology, innovation, and futurism. Your task is to provide relevant information, examples, and data points on the given topic."},
        {"role": "user", "content": f"Please provide key information, examples, and data points relevant to the following topic:\n\n{topic}\n\nInclude specific technologies, companies, or innovations where applicable. When referencing specific sources, use the format 'According to [Source],' to facilitate citation generation."}
    ]
    research_content, research_time = generate_response(research_prompt, "Content Researcher")
    citations = generate_citations(research_content)
    return research_content, citations, research_time

def content_writer(topic, research):
    """Content writer agent to create the main body of the blog post."""
    writer_prompt = [
        {"role": "system", "content": "You are an expert content writer specializing in technology and innovation blog posts. Your task is to create engaging, informative content based on the given topic and research. Write as if for a final publication - do not include any meta-comments, questions to the user, or references to the writing process itself."},
        {"role": "user", "content": f"Write a comprehensive blog post on the following topic:\n\n{topic}\n\nUse the following research to inform your writing:\n\n{research}\n\nEnsure the content is well-structured, engaging, and informative. Use markdown formatting for headers and emphasis. The post should be complete and ready for publication without any additional comments or questions."}
    ]
    blog_content, writing_time = generate_response(writer_prompt, "Content Writer")
    return clean_content(blog_content), writing_time

def editor_review(content):
    """Editor agent to review and refine the content."""
    editor_prompt = [
        {"role": "system", "content": "You are an expert editor specializing in technology and innovation blog posts. Your task is to review and refine the given content, focusing on clarity, coherence, and engagement."},
        {"role": "user", "content": f"Please review and improve the following blog post content:\n\n{content}\n\nFocus on enhancing clarity, ensuring coherence between paragraphs, and making the content more engaging. Provide your edited version in markdown format."}
    ]
    edited_content, edit_time = generate_response(editor_prompt, "Editor")
    return edited_content, edit_time

def fact_checker(content):
    """Fact-checking agent to verify the accuracy of the content."""
    fact_check_prompt = [
        {"role": "system", "content": "You are an expert fact-checker specializing in technology and innovation. Your task is to verify the accuracy of the given content and suggest corrections if needed."},
        {"role": "user", "content": f"Please fact-check the following blog post content:\n\n{content}\n\nIdentify any inaccuracies or questionable claims. Provide corrections or suggestions for improvement where necessary."}
    ]
    fact_check_results, fact_check_time = generate_response(fact_check_prompt, "Fact Checker")
    return fact_check_results, fact_check_time

def final_review(content, fact_check_results, keywords, citations):
    """Final review agent to incorporate fact-check results and add finishing touches."""
    review_prompt = [
        {"role": "system", "content": "You are an expert editor and content reviewer. Your task is to review the given blog post, incorporate fact-check results, and add final touches to improve the overall quality."},
        {"role": "user", "content": f"Please review the following blog post and incorporate the fact-check results:\n\nBlog post:\n{content}\n\nFact-check results:\n{fact_check_results}\n\nExtracted keywords for SEO: {', '.join(keywords)}\n\nMake necessary adjustments, ensuring:\n1. Clarity of ideas\n2. High engagement factor\n3. Effective use of examples and explanations\n4. Appropriateness for a general audience interested in technology and innovation\n5. Proper formatting\n6. A brief, engaging conclusion if it's missing\n7. Natural incorporation of SEO keywords without compromising readability\n8. Inclusion of the following citations at the end of the post:\n\n{citations}\n\nMaintain the content's originality and excitement. Return the final version in markdown format."}
    ]
    final_content, review_time = generate_response(review_prompt, "Final Reviewer")
    return final_content, review_time

def extract_categories(content, num_categories=3):
    """Extract categories from the content."""
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform([content])
    feature_names = vectorizer.get_feature_names_out()
    sorted_items = sorted(zip(tfidf_matrix.tocsc().data, feature_names), key=lambda x: x[0], reverse=True)
    categories = [item[1].capitalize() for item in sorted_items[:num_categories]]
    return categories

def save_blog_post(content, topic):
    """Save the blog post as a Markdown file in the _posts directory with a date-based name and dynamic categories."""
    date_str = datetime.now().strftime("%Y-%m-%d")
    posts_dir = "_posts"
    os.makedirs(posts_dir, exist_ok=True)
    filename = f"{posts_dir}/{date_str}-{topic.replace(' ', '-').lower()[:30]}.md"
    
    categories = extract_categories(content)
    categories_str = ", ".join([f'"{cat}"' for cat in categories])
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("---\n")
        f.write(f"layout: post\n")
        f.write(f"title: \"{topic}\"\n")
        f.write(f"date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} +0000\n")
        f.write(f"categories: [{categories_str}]\n")
        f.write("---\n\n")
        f.write(content)
    return filename, categories

def get_run_count():
    """Get the current run count from a file."""
    if os.path.exists('run_count.txt'):
        with open('run_count.txt', 'r') as f:
            return int(f.read().strip())
    return 0

def increment_run_count():
    """Increment the run count and save it to a file."""
    count = get_run_count() + 1
    with open('run_count.txt', 'w') as f:
        f.write(str(count))
    return count

def clean_content(content):
    """Remove any meta-comments or questions from the content."""
    lines = content.split('\n')
    cleaned_lines = []
    for line in lines:
        if not any(phrase in line.lower() for phrase in ["let me know", "please advise"]):
            cleaned_lines.append(line)
    return '\n'.join(cleaned_lines).strip()

if __name__ == "__main__":
    try:
        run_count = increment_run_count()
        logger.info(f"Starting blog post generation process (Run {run_count}/3)")
        
        if run_count > 3:
            logger.info("Maximum number of runs reached. Exiting.")
            exit(0)
        
        logger.info("Starting creative agents to generate a topic")
        topic = generate_topic(max_iterations=2)
        print(f"\n{Fore.CYAN}Generated Topic: {topic}{Style.RESET_ALL}\n")
        
        logger.info("Starting content research")
        research, citations, research_time = content_researcher(topic)
        
        logger.info("Writing initial blog post content")
        initial_content, writing_time = content_writer(topic, research)
        
        logger.info("Performing editor review")
        edited_content, edit_time = editor_review(initial_content)
        
        logger.info("Fact-checking the content")
        fact_check_results, fact_check_time = fact_checker(edited_content)
        
        logger.info("Extracting keywords for SEO")
        keywords = extract_keywords(edited_content)
        
        logger.info("Performing final review and adding finishing touches")
        final_content, review_time = final_review(edited_content, fact_check_results, keywords, citations)
        
        total_time = research_time + writing_time + edit_time + fact_check_time + review_time
        
        print(f"\n{Fore.YELLOW}Final Blog Post Content:{Style.RESET_ALL}")
        print("=" * 40)
        print(final_content)
        print("=" * 40)
        
        filename, categories = save_blog_post(final_content, topic)
        print(f"\n{Fore.GREEN}Blog post saved as: {filename}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Categories: {', '.join(categories)}{Style.RESET_ALL}")

        print(f"\n{Fore.CYAN}Extracted Keywords for SEO:{Style.RESET_ALL}")
        print(", ".join(keywords))
        
        print(f"\n{Fore.CYAN}Generated Citations:{Style.RESET_ALL}")
        print(citations)
        
        print(f"\n{Fore.CYAN}Time Statistics:{Style.RESET_ALL}")
        print(f"Total API response time: {total_time:.2f} seconds")
        print(f"Research time: {research_time:.2f} seconds")
        print(f"Writing time: {writing_time:.2f} seconds")
        print(f"Editing time: {edit_time:.2f} seconds")
        print(f"Fact-checking time: {fact_check_time:.2f} seconds")
        print(f"Final review time: {review_time:.2f} seconds")
        
        logger.info("Blog post generation completed successfully")
    except Exception as e:
        logger.error(f"An error occurred during blog post generation: {e}")
        raise