import csv
import random
import json

topics = ["Kubernetes", "Machine Learning", "Docker", "Python"]
actions = ["Introduction to", "Advanced techniques for", "Mastering", "Hands-on walkthrough of", "Deep dive into", "Basics of", "Best practices for"]
difficulty_levels = ["Beginner", "Intermediate", "Advanced"]
formats = ["video", "article", "blog"]
tags_pool = ["kubernetes", "ml", "deployment", "docker", "ai", "python", "architecture"]

def generate_dataset(num_rows=100):
    data = []
    for i in range(1, num_rows + 1):
        topic = random.choice(topics)
        action = random.choice(actions)
        title = f"{action} {topic}"
        fmt = random.choice(formats)
        desc_templates = [
            f"This comprehensive {fmt} covers the essential concepts and practical applications of {topic}.",
            f"In this high-yield session, you will learn the ins and outs of {topic} with real-world scenarios.",
            f"Explore the nuances of {topic} through guided, hands-on examples and best practices.",
            f"A detailed and structured guide to mastering {topic} for modern software development."
        ]
        target_audience = random.choice(['software engineers', 'data scientists', 'backend developers', 'frontend developers', 'devops engineers', 'tech leads', 'system architects'])
        outcome = random.choice([
            f"By the end of this material, you will be able to confidently build and deploy with {topic}.",
            f"Expect to gain extensive practical experience with {topic.lower()} workflows and tools.",
            f"This {fmt} is guaranteed to level up your technical skills in {topic.lower()}.",
            f"You will walk away with a solid understanding of how to leverage {topic} in production environments."
        ])
        description = f"{random.choice(desc_templates)} Designed specifically for {target_audience}. {outcome}"
        difficulty = random.choice(difficulty_levels)
        duration = random.choice([15, 30, 45, 60, 90, 120])
        num_tags = random.randint(2, 4)
        tags = random.sample(tags_pool, num_tags)
        url = f"https://example.com/tutorials/{topic.lower().replace(' ', '-')}/{i}"
        
        row = {
            "id": i,
            "title": title,
            "description": description,
            "difficulty": difficulty,
            "duration_minutes": duration,
            "tags": json.dumps(tags), # Storing as JSON string
            "format": fmt,
            "url": url
        }
        data.append(row)
    return data

def main():
    data = generate_dataset(100)
    keys = data[0].keys()
    
    with open('data/sample_data.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(data)
        
    print(f"Successfully generated 100 sample records to sample_data.csv")

if __name__ == "__main__":
    main()
