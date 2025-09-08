Skip to content
Navigation Menu
jaxfourtwenty
jax420-deals

Type / to search
Code
Issues
Pull requests
Actions
Projects
Wiki
Security
Insights
Settings
jax420-deals
/
generate_deals.py
in
main

Edit

Preview
Indent mode

Spaces
Indent size

4
Line wrap mode

No wrap
Editing generate_deals.py file contents
147
148
149
150
151
152
153
154
155
156
157
158
159
160
161
162
163
164
165
166
167
168
169
170
171
172
173
174
175
176
177
178
179
180
181
182
183
184
185
186
187
188
189
190
191
192
193
194
195
196
197
198
199
200
201
202
203
204
205
206
import os
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


Use Control + Shift + m to toggle the tab key moving focus. Alternatively, use esc then tab to move to the next interactive element on the page.
