import os
import logging
import time
from groq import Groq
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize Groq client
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def generate_response(messages, role):
    """Generate a response using the Groq API."""
    try:
        start_time = time.time()
        chat_completion = client.chat.completions.create(
            messages=messages,
            model="llama3-8b-8192",
            max_tokens=500,
            temperature=0.7,
        )
        end_time = time.time()
        response = chat_completion.choices[0].message.content
        return response, end_time - start_time
    except Exception as e:
        logger.error(f"Error generating {role} response: {e}")
        return None, 0

def generate_topic(max_iterations=5):
    """Generate a topic using three creative agents."""
    messages = [
        {"role": "system", "content": f"You are three creative AI agents collaborating to generate an interesting and unique blog post topic. You have {max_iterations} rounds to refine and improve the topic. Be concise and build upon each other's ideas effectively."},
        {"role": "user", "content": "Let's brainstorm an interesting topic for a blog post. Suggest a broad area or theme to start with."}
    ]
    
    for i in range(max_iterations):
        for agent in range(1, 4):
            remaining_iterations = max_iterations - i
            prompt = f"Agent {agent}, consider the previous suggestions and propose a refined or new topic idea. Be creative and specific. We have {remaining_iterations} iterations left, so make your contribution count."
            response, _ = generate_response(messages + [{"role": "user", "content": prompt}], f"Creative Agent {agent}")
            
            if response:
                print(f"{Fore.MAGENTA}Creative Agent {agent}: {response}{Style.RESET_ALL}\n")
                messages.append({"role": "assistant", "content": response})
            else:
                logger.warning(f"Failed to generate response for Creative Agent {agent}. Continuing with next agent.")
            
            time.sleep(1)  # Short delay between agents
    
    # Final topic selection
    final_prompt = "Based on our brainstorming session, what's the most interesting and specific topic we've come up with for the blog post? Provide a concise topic statement."
    final_topic, _ = generate_response(messages + [{"role": "user", "content": final_prompt}], "Topic Selector")
    
    return final_topic.strip() if final_topic else "The impact of technology on modern society"

def self_chat_agent(topic, max_interactions=15):
    """Create a chat agent that talks to itself about a given topic, with an editor reviewing the content."""
    sections = [
        "Introduction",
        "Key Aspects and Analysis",
        "Implications and Conclusion"
    ]
    
    messages = [
        {"role": "system", "content": f"You are two AI assistants collaboratively creating a structured blog post on the given topic. You have a maximum of {max_interactions} total interactions to complete the post. Each response should be concise, focused, and build upon the previous one. Use Markdown formatting for headers, lists, and emphasis. The final output will be saved as a .md file."},
        {"role": "user", "content": f"Let's start writing a structured blog post about {topic}. Begin with the introduction section that captures the reader's attention and outlines the key points we'll discuss. Use proper Markdown syntax for formatting. Remember, we have limited interactions, so be concise and impactful."}
    ]
    
    blog_post = []
    total_time = 0
    edit_time = 0
    interaction_count = 0
    
    for section in sections:
        if interaction_count >= max_interactions:
            break
        
        logger.info(f"Generating content for section: {section}")
        
        remaining_interactions = max_interactions - interaction_count
        
        # Generate Assistant 1 response
        prompt1 = f"Write the {section} section of our blog post. Start with a clear heading and explicitly build upon the previous content. Be concise and focused, as we have {remaining_interactions} interactions left for the entire post."
        response1, time1 = generate_response(messages + [{"role": "user", "content": prompt1}], "Assistant 1")
        total_time += time1
        interaction_count += 1
        
        if response1:
            print(f"{Fore.GREEN}Assistant 1 ({time1:.2f}s): {response1}{Style.RESET_ALL}\n")
            messages.append({"role": "assistant", "content": response1})
            
            if interaction_count >= max_interactions:
                break
            
            remaining_interactions = max_interactions - interaction_count
            
            # Generate Assistant 2 response
            prompt2 = f"Acknowledge the previous content for the {section} section and expand on it. Add depth to the discussion or introduce a related aspect of the topic within this section. Remember, we have {remaining_interactions} interactions left for the entire post."
            response2, time2 = generate_response(messages + [{"role": "user", "content": prompt2}], "Assistant 2")
            total_time += time2
            interaction_count += 1
            
            if response2:
                print(f"{Fore.BLUE}Assistant 2 ({time2:.2f}s): {response2}{Style.RESET_ALL}\n")
                messages.append({"role": "assistant", "content": response2})
                
                # Editor review
                section_content = f"{response1}\n\n{response2}"
                edited_content, edit_time_section = editor_review(section_content)
                edit_time += edit_time_section
                interaction_count += 1
                
                if edited_content:
                    print(f"{Fore.YELLOW}Editor ({edit_time_section:.2f}s): {edited_content}{Style.RESET_ALL}\n")
                    blog_post.append(edited_content)
                else:
                    logger.warning(f"Editor failed to refine content for {section}. Using original content.")
                    blog_post.append(section_content)
            else:
                logger.warning(f"Failed to generate Assistant 2 response for {section}. Moving to next section.")
        else:
            logger.warning(f"Failed to generate Assistant 1 response for {section}. Moving to next section.")
        
        # Add 2-second buffer between sections
        time.sleep(2)
    
    return "\n\n".join(blog_post), total_time, edit_time

def editor_review(content):
    """Editor agent to review and refine the content."""
    editor_prompt = [
        {"role": "system", "content": "You are an expert editor specializing in blog posts about technology and futurism. Your task is to review and refine the given content, focusing on clarity, coherence, and engagement."},
        {"role": "user", "content": f"Please review and improve the following content:\n\n{content}\n\nFocus on enhancing clarity, ensuring coherence between paragraphs, and making the content more engaging. Provide your edited version."}
    ]
    edited_content, edit_time = generate_response(editor_prompt, "Editor")
    return edited_content, edit_time

def final_review(content):
    """Final review agent to check format and add finishing touches."""
    review_prompt = [
        {"role": "system", "content": "You are an expert editor and content reviewer. Your task is to review the given blog post, ensure proper formatting, and add a final touch if needed."},
        {"role": "user", "content": f"Please review the following blog post:\n\n{content}\n\nEnsure proper formatting, check for coherence between sections, and add a brief, engaging conclusion if it's missing. Return the revised version."}
    ]
    revised_content, review_time = generate_response(review_prompt, "Final Reviewer")
    return revised_content, review_time

def markdown_review(content):
    """Review and adjust the content for Markdown formatting."""
    review_prompt = [
        {"role": "system", "content": "You are an expert in Markdown formatting. Your task is to review the given blog post content and ensure it adheres to proper Markdown syntax and style."},
        {"role": "user", "content": f"Please review the following blog post content and adjust it for Markdown formatting:\n\n{content}\n\nEnsure proper use of headers, lists, emphasis, and other Markdown elements. Make any necessary adjustments to improve readability and structure in Markdown format."}
    ]
    revised_content, review_time = generate_response(review_prompt, "Markdown Reviewer")
    return revised_content, review_time

def save_blog_post(content, topic):
    """Save the blog post as a Markdown file with a unique name."""
    base_filename = f"blog_post_{topic.replace(' ', '_').lower()[:30]}"
    counter = 1
    while True:
        filename = f"{base_filename}_{counter}.md"
        if not os.path.exists(filename):
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            return filename
        counter += 1

if __name__ == "__main__":
    max_total_interactions = 20
    
    logger.info("Starting creative agents to generate a topic")
    topic = generate_topic(max_iterations=3)
    print(f"\n{Fore.CYAN}Generated Topic: {topic}{Style.RESET_ALL}\n")
    
    logger.info(f"Starting self-chat agent to create a structured blog post about {topic}")
    
    start_time = time.time()
    blog_post, api_time, edit_time = self_chat_agent(topic, max_interactions=max_total_interactions - 3)  # Subtract topic generation interactions
    
    logger.info("Performing final review and adding finishing touches")
    final_blog_post, review_time = final_review(blog_post)
    api_time += review_time
    
    logger.info("Reviewing and adjusting Markdown formatting")
    markdown_blog_post, markdown_time = markdown_review(final_blog_post)
    api_time += markdown_time
    
    total_time = time.time() - start_time
    
    print(f"\n{Fore.YELLOW}Final Structured Blog Post (Markdown):{Style.RESET_ALL}")
    print("=" * 40)
    print(markdown_blog_post)
    print("=" * 40)
    
    filename = save_blog_post(markdown_blog_post, topic)
    print(f"\n{Fore.GREEN}Blog post saved as: {filename}{Style.RESET_ALL}")
    
    print(f"\n{Fore.CYAN}Time Statistics:{Style.RESET_ALL}")
    print(f"Total execution time: {total_time:.2f} seconds")
    print(f"API response time: {api_time:.2f} seconds")
    print(f"Editor time: {edit_time:.2f} seconds")
    print(f"Overhead time: {total_time - api_time - edit_time:.2f} seconds")
    
    logger.info("Structured blog post generation completed.")