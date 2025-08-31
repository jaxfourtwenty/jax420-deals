import os
import datetime
import openai

# Load OpenAI API key from environment variables
openai.api_key = os.environ.get("OPENAI_API_KEY")

# Get today's date in America/New_York timezone
now = datetime.datetime.now(datetime.timezone.utc).astimezone(datetime.timezone(datetime.timedelta(hours=-4)))
# Format date as M/D/YYYY
if hasattr(now, "strftime"):
    date_str = now.strftime("%-m/%-d/%Y")
else:
    # Fallback if %-m is not available
    date_str = now.strftime("%m/%d/%Y")

# Construct the prompt with the current date
prompt = f"""
FORMAT REQUIREMENT: Return the answer inside a single fenced code block (use ```markdown) with “raw” Carrd formatting — no commentary outside the block, no citations, no bullets, no numbering.

Sample line with clickable name (match spacing/punctuation exactly):
[**Fluent – Jacksonville**](https://fluentfl.com) — “High Vibes Low Prices” up to 60 % off most products; valid Jul 25–31.

Headings to use verbatim (with emojis), in this order, each separated by one blank line:
**🔥 TODAY’S HOT DEALS  🔥**
**🔥 BEST PREROLL DEALS 🔥**
**🌳 BEST FLOWER DEALS 🌳**
**☀ BEST DISTILLATE DEALS ☀**
**🧊 BEST VAPE CART DEALS 🧊**
**🧴 BEST TOPICAL DEALS 🧴**
**🍭 BEST EDIBLE DEALS 🍭**

COUNT REQUIREMENTS:
* TODAY’S HOT DEALS — include 8–10 lines.
* All other categories — include 3–5 lines each.

SCOPE & ELIGIBILITY:
* CITY: Jacksonville, Florida metro (Jacksonville proper preferred; nearby 904 areas like Jacksonville Beach/Orange Park acceptable if needed).
* DATE: {date_str}. Include any promo that is valid on {date_str} (single-day or multi-day), but exclude veteran-only, new-patient, employee, points-only, or invite/text-exclusive offers.
* Each line must state the validity window at the end (e.g., “valid Aug 2” or “valid Aug 1–3”).

LINE FORMAT (exact):
[**{{Dispensary Name}} – {{City/Neighborhood}}**](https://{{official-dispensary-website}}) — “{{Promo title or short description}}” {{concise details}}; valid {{Date or Date Range}}.

LINK RULES (very important):
* Link ONLY the bolded dispensary name + location using standard Markdown link syntax as shown above.
* Use the official dispensary/brand website (homepage or the Florida/Jacksonville store page if available). No third-party menus (Leafly/Weedmaps/etc.) unless no official site exists; if unclear, default to the brand homepage.
* Use clean https URLs with no tracking parameters (no UTM, referral codes, or anchors).
* Do not place any other links anywhere else in the line.

STYLE RULES:
* Use double asterisks for bold around the dispensary name and location (inside the link).
* Use the spaced em dash exactly like this: space, —, space.
* Use straight quotes around promo titles and keep details short (numbers, % off, quantities).
* Use symbols where appropriate: ½, ¼, × for multipliers.
* No extra text outside the code block and no additional links beyond the clickable dispensary name.

SEARCH TASK:
* Search current Jacksonville (FL) dispensary specials valid on {date_str}.
* Verify dates on official brand/dispensary sources; if unclear, omit the deal.
* Avoid duplicates and clearly specify product type when needed (flower, pre-roll, vape, edible, topical, concentrates/distillate).

OUTPUT:
* Return only the code block with the seven headings and their lines, with the dispensary names hyperlinked as specified, ready to paste into Carrd.

OPTIONAL DOMAIN MAP (use if applicable; otherwise default to brand homepage):
- Curaleaf → https://curaleaf.com
- MÜV → https://muvfl.com
- Trulieve → https://www.trulieve.com
- AYR → https://ayrcannabis.com
- Surterra → https://www.surterra.com
- Fluent → https://fluentfl.com
- Sunburn → https://sunburncannabis.com
- GrowHealthy → https://growhealthy.com
- Cookies → https://cookies.co
- Green Dragon → https://greendragon.com
- Sanctuary → https://sanctuarycannabis.com
- VidaCann → https://www.vidacann.com
"""

# Call OpenAI ChatCompletion API to get the deals block
response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[{"role": "user", "content": prompt}],
    temperature=0.0
)

# Extract the content
content = response.choices[0].message["content"]

# Extract the markdown code block
start = content.find("```markdown")
end = content.find("```", start + 3)
if start != -1 and end != -1:
    deals_block = content[start + len("```markdown"):end].strip()
else:
    deals_block = content.strip()

# Escape HTML special characters and wrap inside <pre>
escaped = deals_block.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
html_content = f"<pre>{escaped}</pre>\n"

# Write full block to index.html
with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_content)

# Define sections with proper emoji headings
sections = {
    "🔥 TODAY’S HOT DEALS  🔥": "todayshotdeals.html",
    "🔥 BEST PREROLL DEALS 🔥": "bestprerolldeals.html",
    "🌳 BEST FLOWER DEALS 🌳": "bestflowerdeals.html",
    "☀ BEST DISTILLATE DEALS ☀": "bestdistillatedeals.html",
    "🧊 BEST VAPE CART DEALS 🧊": "bestvapecartdeals.html",
    "🧴 BEST TOPICAL DEALS 🧴": "besttopicaldeals.html",
    "🍭 BEST EDIBLE DEALS 🍭": "bestedibledeals.html"
}

# Initialize lines for each section
section_lines = {heading: [] for heading in sections}
current_section = None

# Go through each line and assign to appropriate section
for line in deals_block.split("\n"):
    stripped = line.strip()
    # Check if this line is a heading
    for heading in sections:
        # Remove markdown bold syntax for matching
        plain_heading = heading
        if plain_heading in stripped:
            current_section = heading
            break
    else:
        if current_section:
            # Add non-empty lines to the current section
            if stripped:
                section_lines[current_section].append(stripped)

# Write each section to its corresponding HTML file
for heading, filename in sections.items():
    lines = section_lines[heading]
    if lines:
        section_content = "\n".join(lines)
        # Escape HTML
        escaped_section = section_content.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        section_html = f"<pre>{escaped_section}</pre>\n"
    else:
        section_html = "<pre>No deals found.</pre>\n"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(section_html)

# Write date to date.html
with open("date.html", "w", encoding="utf-8") as f:
    f.write(now.strftime("%B %d, %Y"))
    # Escape HTML special characters and wrap inside <pre>
escaped = deals_block.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
html_content = f"<pre>{escaped}</pre>\n"

# Write full block to index.html
with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_content)

# Define sections with proper emoji headings
sections = {
    "🔥 TODAY’S HOT DEALS  🔥": "todayshotdeals.html",
    "🔥 BEST PREROLL DEALS 🔥": "bestprerolldeals.html",
    "🌳 BEST FLOWER DEALS 🌳": "bestflowerdeals.html",
    "☀ BEST DISTILLATE DEALS ☀": "bestdistillatedeals.html",
    "🧊 BEST VAPE CART DEALS 🧊": "bestvapecartdeals.html",
    "🧴 BEST TOPICAL DEALS 🧴": "besttopicaldeals.html",
    "🍭 BEST EDIBLE DEALS 🍭": "bestedibledeals.html"
}

# Initialize lines for each section
section_lines = {heading: [] for heading in sections}
current_section = None

# Go through each line and assign to appropriate section
for line in deals_block.split("\n"):
    stripped = line.strip()
    # Check if this line is a heading
    for heading in sections:
        # Remove markdown bold syntax for matching
        plain_heading = heading
        if plain_heading in stripped:
            current_section = heading
            break
    else:
        if current_section:
            # Add non-empty lines to the current section
            if stripped:
                section_lines[current_section].append(stripped)

# Write each section to its corresponding HTML file
for heading, filename in sections.items():
    lines = section_lines[heading]
    if lines:
        section_content = "\n".join(lines)
        # Escape HTML
        escaped_section = section_content.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        section_html = f"<pre>{escaped_section}</pre>\n"
    else:
        section_html = "<pre>No deals found.</pre>\n"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(section_html)

# Write date to date.html
with open("date.html", "w", encoding="utf-8") as f:
    f.write(now.strftimeimport os, datetime
import openai

# Load OpenAI API key from environment
openai.api_key = os.environ["OPENAI_API_KEY"]

# Get today’s date in Eastern Time (America/New_York)
now = datetime.datetime.now(datetime.timezone.utc).astimezone(
    datetime.timezone(datetime.timedelta(hours=-4))
)
date_str = now.strftime("%-m/%-d/%Y") if hasattr(now, "strftime") else now.strftime("%m/%d/%Y")

# Construct prompt for ChatGPT with current date
prompt = f"""
FORMAT REQUIREMENT: Return the answer inside a single fenced code block (use ```markdown) with “raw” Carrd formatting — no commentary outside the block, no citations, no bullets, no numbering.

Sample line with clickable name (match spacing/punctuation exactly):
[**Fluent – Jacksonville**](https://fluentfl.com) — “High Vibes Low Prices” up to 60 % off most products; valid Jul 25–31.

Headings to use verbatim (with emojis), in this order, each separated by one blank line:
**🔥 TODAY’S HOT DEALS  🔥**
**🔥 BEST PREROLL DEALS 🔥**
**🌳 BEST FLOWER DEALS 🌳**
**☀ BEST DISTILLATE DEALS ☀**
**🎈 BEST VAPE CART DEALS 🎈**
**🕴 BEST TOPICAL DEALS 🕴**
**🍭 BEST EDIBLE DEALS 🍭**

COUNT REQUIREMENTS:
* TODAY’S HOT DEALS — include 8–10 lines.
* All other categories — include 3–5 lines each.

SCOPE & ELIGIBILITY:
* CITY: Jacksonville, Florida metro (Jacksonville proper preferred; nearby 904 areas like Jacksonville Beach/Orange Park acceptable if needed).
* DATE: {date_str}. Include any promo that is valid on {date_str} (single-day or multi-day), but exclude veteran-only, new-patient, employee, points-only, or invite/text-exclusive offers.
* Each line must state the validity window at the end (e.g., “valid Aug 2” or “valid Aug 1–3”).

LINE FORMAT (exact):
[**{{Dispensary Name}} – {{City/Neighborhood}}**](https://{{official-dispensary-website}}) — “{{Promo title or short description}}” {{concise details}}; valid {{Date or Date Range}}.

LINK RULES (very important):
* Link ONLY the bolded dispensary name + location using standard Markdown link syntax as shown above.
* Use the official dispensary/brand website (homepage or the Florida/Jacksonville store page if available). No third-party menus (Leafly/Weedmaps/etc.) unless no official site exists; if unclear, default to the brand homepage.
* Use clean https URLs with no tracking parameters (no UTM, referral codes, or anchors).
* Do not place any other links anywhere else in the line.

STYLE RULES:
* Use double asterisks for bold around the dispensary name and location (inside the link).
* Use the spaced em dash exactly like this: space, —, space.
* Use straight quotes around promo titles and keep details short (numbers, % off, quantities).
* Use symbols where appropriate: ½, ¼, × for multipliers.
* No extra text outside the code block and no additional links beyond the clickable dispensary name.

SEARCH TASK:
* Search current Jacksonville (FL) dispensary specials valid on {date_str}.
* Verify dates on official brand/dispensary sources; if unclear, omit the deal.
* Avoid duplicates and clearly specify product type when needed (flower, pre-roll, vape, edible, topical, concentrates/distillate).

OUTPUT:
* Return only the code block with the seven headings and their lines, with the dispensary names hyperlinked as specified, ready to paste into Carrd.

OPTIONAL DOMAIN MAP (use if applicable; otherwise default to brand homepage):
- Curaleaf → https://curaleaf.com
- MÜV → https://muvfl.com
- Trulieve → https://www.trulieve.com
- AYR → https://ayrcannabis.com
- Surterra → https://www.surterra.com
- Fluent → https://fluentfl.com
- Sunburn → https://sunburncannabis.com
- GrowHealthy → https://growhealthy.com
- Cookies → https://cookies.co
- Green Dragon → https://greendragon.com
- Sanctuary → https://sanctuarycannabis.com
- VidaCann → https://www.vidacann.com
"""

# Call OpenAI ChatCompletion API to get the deals block
response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[{"role": "user", "content": prompt}],
    temperature=0.0
)

content = response.choices[0].message["content"]
# Extract the markdown code block
start = content.find("```markdown")
end = content.find("```", start + 3)
if start != -1 and end != -1:
    deals_block = content[start + len("```markdown"):end].strip()
else:
    deals_block = content.strip()

# Escape HTML special characters and wrap inside <pre>
escaped = deals_block.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
html_content = f"<pre>{escaped}</pre>\n"

# Overwrite index.html
with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_content)
