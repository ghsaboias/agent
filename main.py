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

def editor_review(content):
    """Editor agent to review and refine the content."""
    editor_prompt = [
        {"role": "system", "content": "You are an expert editor specializing in blog posts about technology and futurism. Your task is to review and refine the given content, focusing on clarity, coherence, and engagement."},
        {"role": "user", "content": f"Please review and improve the following content:\n\n{content}\n\nFocus on enhancing clarity, ensuring coherence between paragraphs, and making the content more engaging. Provide your edited version."}
    ]
    edited_content, edit_time = generate_response(editor_prompt, "Editor")
    return edited_content, edit_time

def self_chat_agent(topic, num_iterations=5):
    """Create a chat agent that talks to itself about a given topic, with an editor reviewing the content."""
    sections = [
        "Introduction",
        "What is the Technological Singularity?",
        "Potential Triggers of the Singularity",
        "Implications for Society and Humanity",
        "Ethical Considerations",
        "Conclusion"
    ]
    
    messages = [
        {"role": "system", "content": "You are two AI assistants collaboratively creating a structured blog post about the singularity. Each response should explicitly acknowledge and build upon the previous one, focusing on clarity, depth, and engaging content. Use clear section headings and maintain a coherent structure throughout the post."},
        {"role": "user", "content": f"Let's start writing a structured blog post about {topic}. Begin with the introduction section that captures the reader's attention and outlines the key points we'll discuss."}
    ]
    
    blog_post = []
    total_time = 0
    edit_time = 0
    
    for section in sections:
        logger.info(f"Generating content for section: {section}")
        
        # Generate Assistant 1 response
        prompt1 = f"Write the {section} section of our blog post. Start with a clear heading and explicitly build upon the previous content. Introduce new insights or perspectives relevant to this section."
        response1, time1 = generate_response(messages + [{"role": "user", "content": prompt1}], "Assistant 1")
        total_time += time1
        
        if response1:
            print(f"{Fore.GREEN}Assistant 1 ({time1:.2f}s): {response1}{Style.RESET_ALL}\n")
            messages.append({"role": "assistant", "content": response1})
            
            # Add 2-second buffer
            time.sleep(2)
            
            # Generate Assistant 2 response
            prompt2 = f"Acknowledge the previous content for the {section} section and expand on it. Add depth to the discussion or introduce a related aspect of the topic within this section."
            response2, time2 = generate_response(messages + [{"role": "user", "content": prompt2}], "Assistant 2")
            total_time += time2
            
            if response2:
                print(f"{Fore.BLUE}Assistant 2 ({time2:.2f}s): {response2}{Style.RESET_ALL}\n")
                messages.append({"role": "assistant", "content": response2})
                
                # Add 2-second buffer
                time.sleep(2)
                
                # Editor review
                section_content = f"{response1}\n\n{response2}"
                edited_content, edit_time_section = editor_review(section_content)
                edit_time += edit_time_section
                
                if edited_content:
                    print(f"{Fore.YELLOW}Editor ({edit_time_section:.2f}s): {edited_content}{Style.RESET_ALL}\n")
                    blog_post.append(edited_content)
                else:
                    logger.warning(f"Editor failed to refine content for {section}. Using original content.")
                    blog_post.append(section_content)
                
                # Add 2-second buffer
                time.sleep(2)
            else:
                logger.warning(f"Failed to generate Assistant 2 response for {section}. Moving to next section.")
        else:
            logger.warning(f"Failed to generate Assistant 1 response for {section}. Moving to next section.")
        
        # Add 2-second buffer between sections
        time.sleep(2)
    
    return "\n\n".join(blog_post), total_time, edit_time

if __name__ == "__main__":
    topic = "the technological singularity and its potential impact on humanity"
    logger.info(f"Starting self-chat agent to create a structured blog post about {topic}")
    
    start_time = time.time()
    blog_post, api_time, edit_time = self_chat_agent(topic)
    total_time = time.time() - start_time
    
    print(f"\n{Fore.YELLOW}Final Structured Blog Post:{Style.RESET_ALL}")
    print("=" * 40)
    print(blog_post)
    print("=" * 40)
    
    print(f"\n{Fore.CYAN}Time Statistics:{Style.RESET_ALL}")
    print(f"Total execution time: {total_time:.2f} seconds")
    print(f"API response time: {api_time:.2f} seconds")
    print(f"Editor time: {edit_time:.2f} seconds")
    print(f"Overhead time: {total_time - api_time - edit_time:.2f} seconds")
    
    logger.info("Structured blog post generation completed.")