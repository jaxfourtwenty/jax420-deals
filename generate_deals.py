import os
import datetime
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def fetch_deals():
    now = datetime.datetime.now()
    date_str = now.strftime("%B %d, %Y")
    instructions = (
        "You are an aggregator of weed deals for Jacksonville, Florida. "
        "Compile a list of the best deals from local dispensaries for {date}. "
        "Include categories with headings like: 🍪 TODAY'S HOT DEALS 🔥, 🥐 BEST PRE-ROLL DEALS 🔥, "
        "🌿 BEST FLOWER DEALS 🍊, 🜠 BEST DISTILLATE DEALS 🜠, 💊 BEST VAPE CART DEALS 💊, "
        "🐆 BEST TOPICAL DEALS 🐆, 🍫 BEST EDIBLE DEALS 🍫. "
        "For each category, list bullet points describing the deals. "
        "Do not add any commentary or content outside the deals list."
    ).format(date=date_str)

    messages = [
        {"role": "system", "content": "You are an expert deals aggregator."},
        {"role": "user", "content": instructions},
    ]

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        max_tokens=2048,
        temperature=0.7,
    )
    return response.choices[0].message.content.strip()

def generate_html(deals_block):
    now = datetime.datetime.now()
    with open("date.html", "w", encoding="utf-8") as f:
        f.write(now.strftime("%B %d, %Y"))

    escaped = (deals_block.replace("&", "&amp;")
                            .replace("<", "&lt;")
                            .replace(">", "&gt;"))
    html_content = f"<pre>{escaped}</pre>\n"

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)

    sections = {
        "🍪 TODAY'S HOT DEALS 🔥": "todayshotdeals.html",
        "🥐 BEST PRE-ROLL DEALS 🔥": "bestprerolldeals.html",
        "🌿 BEST FLOWER DEALS 🍊": "bestflowerdeals.html",
        "🜠 BEST DISTILLATE DEALS 🜠": "bestdistillatedeals.html",
        "💊 BEST VAPE CART DEALS 💊": "bestvapecartdeals.html",
        "🐆 BEST TOPICAL DEALS 🐆": "besttopicaldeals.html",
        "🍫 BEST EDIBLE DEALS 🍫": "bestedibledeals.html",
    }

    section_lines = {heading: [] for heading in sections}
    current_section = None

    for line in deals_block.split("\n"):
        stripped = line.strip()
        matched_heading = None
        for heading in sections:
            if heading in stripped:
                matched_heading = heading
                break
        if matched_heading:
            current_section = matched_heading
            continue
        if current_section and stripped:
            section_lines[current_section].append(stripped)

    for heading, filename in sections.items():
        lines = section_lines[heading]
        if lines:
            section_content = "\n".join(lines)
            escaped_section = (section_content.replace("&", "&amp;")
                                             .replace("<", "&lt;")
                                             .replace(">", "&gt;"))
            section_html = f"<pre>{escaped_section}</pre>\n"
        else:
            section_html = "<pre>No deals found.</pre>\n"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(section_html)

def main():
    deals_block = fetch_deals()
    generate_html(deals_block)

if __name__ == "__main__":
    main()
