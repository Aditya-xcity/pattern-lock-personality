import tkinter as tk
import json
import random
import math
from collections import Counter


class PatternLock:
    def __init__(self):
        self.pattern = []
        self.nodes = {}
        self.radius = 20
        self.correct_pattern = [1, 2, 5, 8]
        self.pattern_history = []
        self.attempts = 0
        self.max_attempts = 5
        self.locked = False          # BUG 8 FIX: flag to block input during reset delay
        self.min_pattern_length = 2  # BUG 9 FIX: require at least 2 nodes

        # Load personality data
        try:
            with open("patternNature.json") as f:
                self.nature_data = json.load(f)
        except FileNotFoundError:
            print("Warning: patternNature.json not found. Using default data.")
            self.nature_data = {
                "line":    ["You are a direct thinker. You cut through complexity and get straight to the point."],
                "zigzag":  ["You are creative and adaptive. You thrive when navigating change."],
                "square":  ["You value stability and structure. You are reliable and thorough."],
                "l_shape": ["You are practical and focused. You pivot decisively when needed."],
                "random":  ["You are spontaneous and open-minded. You embrace the unexpected."],
            }

        self.root = tk.Tk()
        self.root.title("Pattern Lock Personality Test")
        self.root.resizable(False, False)

        main_frame = tk.Frame(self.root, padx=20, pady=20)
        main_frame.pack()

        title = tk.Label(main_frame, text="🔐 Draw Your Pattern",
                         font=("Arial", 16, "bold"))
        title.pack(pady=(0, 10))

        subtitle = tk.Label(main_frame,
                            text="Discover your personality through patterns",
                            font=("Arial", 10, "italic"), fg="gray")
        subtitle.pack(pady=(0, 10))

        self.canvas = tk.Canvas(main_frame, width=400, height=400,
                                bg="lightgrey", highlightthickness=2,
                                highlightbackground="gray")
        self.canvas.pack()

        status_frame = tk.Frame(main_frame)
        status_frame.pack(fill=tk.X, pady=10)

        self.status_label = tk.Label(status_frame, text="Draw your pattern",
                                     font=("Arial", 10))
        self.status_label.pack(side=tk.LEFT)

        self.attempts_label = tk.Label(
            status_frame,
            text=f"Attempts: {self.attempts}/{self.max_attempts}",
            font=("Arial", 10))
        self.attempts_label.pack(side=tk.RIGHT)

        self.insight_text = tk.Text(main_frame, height=4, width=50,
                                    font=("Arial", 10), wrap=tk.WORD,
                                    bg="#f0f0f0", relief=tk.FLAT)
        self.insight_text.pack(pady=10)
        self.insight_text.insert("1.0", "Your personality insight will appear here...")
        self.insight_text.config(state=tk.DISABLED)

        button_frame = tk.Frame(main_frame)
        button_frame.pack()

        self.reset_btn = tk.Button(button_frame, text="Clear Pattern",
                                   command=self.reset_pattern,
                                   bg="#ff6b6b", fg="white")
        self.reset_btn.pack(side=tk.LEFT, padx=5)

        self.analyze_btn = tk.Button(button_frame, text="Analyze Only",
                                     command=self.analyze_current_pattern,
                                     bg="#4ecdc4", fg="white")
        self.analyze_btn.pack(side=tk.LEFT, padx=5)

        self.create_nodes()
        self.setup_bindings()

    # ------------------------------------------------------------------
    # Node creation
    # ------------------------------------------------------------------

    def create_nodes(self):
        """Create the 3×3 grid of nodes."""
        num = 1
        for row in range(3):
            for col in range(3):
                x = 100 + col * 100
                y = 100 + row * 100
                self.nodes[num] = (x, y)

                # Outer circle
                self.canvas.create_oval(
                    x - self.radius, y - self.radius,
                    x + self.radius, y + self.radius,
                    fill="white", outline="#666", width=2,
                    tags=f"node_{num}")

                # Inner highlight ring
                self.canvas.create_oval(
                    x - self.radius + 3, y - self.radius + 3,
                    x + self.radius - 3, y + self.radius - 3,
                    fill="#e0e0e0", outline="",
                    tags=f"node_{num}")

                # Number label — tagged separately so we can always raise it
                self.canvas.create_text(
                    x, y, text=str(num),
                    font=("Arial", 14, "bold"), fill="#333",
                    tags=f"label_{num}")

                num += 1

    # ------------------------------------------------------------------
    # Node detection
    # ------------------------------------------------------------------

    def detect_node(self, x, y):
        """Return the node number whose circle contains (x, y), or None."""
        for n, (nx, ny) in self.nodes.items():
            if (x - nx) ** 2 + (y - ny) ** 2 <= self.radius ** 2:
                return n
        return None

    # ------------------------------------------------------------------
    # Drawing helpers
    # ------------------------------------------------------------------

    def draw_pattern_line(self, start_node, end_node):
        """Draw a permanent connector line between two nodes."""
        x1, y1 = self.nodes[start_node]
        x2, y2 = self.nodes[end_node]
        self.canvas.create_line(
            x1, y1, x2, y2,
            fill="#4a90e2", width=4,
            tags="pattern_line",
            capstyle=tk.ROUND)
        # Direction dot at the destination
        self.canvas.create_oval(
            x2 - 6, y2 - 6, x2 + 6, y2 + 6,
            fill="#4a90e2", outline="white", width=2,
            tags="pattern_line")

    def draw_rubber_band(self, x, y):
        """Draw a temporary line from the last node to the cursor."""
        self.canvas.delete("rubber_band")
        if self.pattern:
            x1, y1 = self.nodes[self.pattern[-1]]
            self.canvas.create_line(
                x1, y1, x, y,
                fill="#4a90e2", width=2, dash=(4, 4),
                tags="rubber_band")

    def highlight_node(self, node):
        """Visually activate a node that has been added to the pattern."""
        x, y = self.nodes[node]

        # BUG 2 FIX: tags were "highlight_{node}" but reset deleted "highlight"
        # Now we use a consistent tag per node AND delete it before re-drawing.
        tag = f"hl_{node}"
        self.canvas.delete(tag)

        # Glow ring
        self.canvas.create_oval(
            x - self.radius - 3, y - self.radius - 3,
            x + self.radius + 3, y + self.radius + 3,
            outline="#4a90e2", width=3, tags=tag)

        # BUG 5 FIX: fill the oval so it covers the original node drawing,
        # preventing double-label artifacts.
        self.canvas.create_oval(
            x - self.radius + 2, y - self.radius + 2,
            x + self.radius - 2, y + self.radius - 2,
            fill="#87CEEB", outline="#4a90e2", width=2, tags=tag)

        # Raise the existing number label on top so it's never hidden
        self.canvas.tag_raise(f"label_{node}")

    def restore_node(self, node):
        """Return a node to its idle appearance."""
        tag = f"hl_{node}"
        self.canvas.delete(tag)
        # Raise the permanent label so it stays visible
        self.canvas.tag_raise(f"label_{node}")

    # ------------------------------------------------------------------
    # Pattern classification
    # ------------------------------------------------------------------

    def detect_pattern_type(self):
        """Classify the drawn pattern into a personality-relevant shape."""
        if len(self.pattern) < 2:
            return "line"

        coords = [self.nodes[n] for n in self.pattern]
        directions = []
        angles = []

        for i in range(len(coords) - 1):
            dx = coords[i + 1][0] - coords[i][0]
            dy = coords[i + 1][1] - coords[i][1]
            # BUG 1 FIX: both branches previously appended "horizontal".
            # Now left/right and up/down are distinguished correctly.
            if abs(dx) > abs(dy):
                directions.append("right" if dx > 0 else "left")
            else:
                directions.append("down" if dy > 0 else "up")

        # Angles between consecutive segments
        for i in range(len(coords) - 2):
            v1 = (coords[i + 1][0] - coords[i][0],
                  coords[i + 1][1] - coords[i][1])
            v2 = (coords[i + 2][0] - coords[i + 1][0],
                  coords[i + 2][1] - coords[i + 1][1])
            len1 = math.sqrt(v1[0] ** 2 + v1[1] ** 2)
            len2 = math.sqrt(v2[0] ** 2 + v2[1] ** 2)
            if len1 > 0 and len2 > 0:
                dot = (v1[0] * v2[0] + v1[1] * v2[1]) / (len1 * len2)
                angle = math.acos(max(-1.0, min(1.0, dot))) * 180 / math.pi
                angles.append(angle)

        # --- Classification ---

        # BUG 7 FIX: for short patterns the angles list may be empty.
        # Guard every angle check with a truth-test first.
        if len(self.pattern) <= 3:
            if len(set(directions)) == 1:
                return "line"
            # angles list has at most 1 entry here
            if angles and any(a > 45 for a in angles):
                return "l_shape"
            return "random"

        # Longer patterns (4+ nodes, angles list has 2+ entries)
        if all(a < 30 for a in angles):
            return "line"
        if any(a > 80 for a in angles):
            if len(set(self.pattern[:4])) >= 4:
                return "square"
            return "l_shape"
        if any(30 <= a <= 70 for a in angles):
            return "zigzag"
        return "random"

    # ------------------------------------------------------------------
    # Complexity score
    # ------------------------------------------------------------------

    def analyze_pattern_complexity(self):
        """Return a numeric complexity score for the drawn pattern."""
        if len(self.pattern) < 2:
            return 0.0

        total_distance = 0.0
        for i in range(len(self.pattern) - 1):
            x1, y1 = self.nodes[self.pattern[i]]
            x2, y2 = self.nodes[self.pattern[i + 1]]
            total_distance += math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

        # Node reuse penalty (drag() prevents it, but guard anyway)
        node_counts = Counter(self.pattern)
        reuse_penalty = sum(c - 1 for c in node_counts.values())

        base_complexity = total_distance / 100
        return base_complexity * (1 + reuse_penalty * 0.5)

    # ------------------------------------------------------------------
    # Personality insight
    # ------------------------------------------------------------------

    def get_personality_insight(self):
        """Build and return a personality insight string."""
        if not self.pattern:
            return "Draw a pattern to discover your personality!"

        pattern_type = self.detect_pattern_type()
        complexity = self.analyze_pattern_complexity()

        traits = self.nature_data.get(pattern_type, ["You are uniquely yourself."])
        selected_trait = random.choice(traits)

        insight = f"🎯 Pattern Type: {pattern_type.upper()}\n\n"
        insight += f"✨ {selected_trait}\n\n"

        if complexity > 8:
            insight += "💭 You enjoy complex challenges and detailed thinking."
        elif complexity > 4:
            insight += "💭 You have a balanced approach to problems."
        else:
            insight += "💭 You prefer straightforward solutions."

        return insight

    def show_personality(self):
        """Display the personality insight in the text widget and console."""
        insight = self.get_personality_insight()

        self.insight_text.config(state=tk.NORMAL)
        self.insight_text.delete("1.0", tk.END)
        self.insight_text.insert("1.0", insight)
        self.insight_text.config(state=tk.DISABLED)

        self.pattern_history.append({
            "pattern": self.pattern.copy(),
            "type":    self.detect_pattern_type(),
            "length":  len(self.pattern),
        })

        print("\n" + "=" * 40)
        print("PATTERN ANALYSIS")
        print("=" * 40)
        print(f"Pattern:    {' → '.join(map(str, self.pattern))}")
        print(f"Type:       {self.detect_pattern_type()}")
        print(f"Complexity: {self.analyze_pattern_complexity():.2f}")
        print(insight)

    # ------------------------------------------------------------------
    # Mouse event handlers
    # ------------------------------------------------------------------

    def drag(self, event):
        """Handle mouse-drag: add nodes to the pattern and draw live line."""
        if self.locked:          # BUG 8 FIX: ignore input while resetting
            return

        # BUG 3 FIX: draw rubber-band line to cursor at every drag event
        self.draw_rubber_band(event.x, event.y)

        node = self.detect_node(event.x, event.y)
        if node and node not in self.pattern:
            if self.pattern:
                self.draw_pattern_line(self.pattern[-1], node)
            self.pattern.append(node)
            self.highlight_node(node)
            self.status_label.config(
                text=f"Pattern: {' → '.join(map(str, self.pattern))}")

    def release(self, event):
        """Handle mouse-release: validate, analyse, then reset for next draw."""
        if self.locked:           # BUG 8 FIX
            return

        self.canvas.delete("rubber_band")

        # BUG 9 FIX: ignore trivially short patterns
        if len(self.pattern) < self.min_pattern_length:
            self.reset_pattern()
            return

        self.attempts += 1
        self.attempts_label.config(
            text=f"Attempts: {self.attempts}/{self.max_attempts}")

        self.canvas.delete("message")

        if self.pattern == self.correct_pattern:
            message, color = "✓ ACCESS GRANTED", "#2ecc71"
            self.status_label.config(text="Access Granted!", fg="green")
        else:
            message, color = "✗ WRONG PATTERN", "#e74c3c"
            self.status_label.config(text="Access Denied!", fg="red")

        self.canvas.create_text(
            200, 50, text=message,
            fill=color, font=("Arial", 18, "bold"),
            tags="message")

        self.show_personality()

        # BUG 4 FIX: clear the drawn pattern so the next drag starts fresh.
        # We keep the highlight/lines visible briefly so the user can see the
        # result, then wipe them when reset_all fires (or immediately on clear).
        if self.attempts >= self.max_attempts:
            # BUG 8 FIX: lock input for the delay window
            self.locked = True
            self.root.after(2000, self.reset_all)
        else:
            # Allow the user to see their pattern for a moment, then clear
            self.root.after(800, self._clear_drawn_pattern)

    def _clear_drawn_pattern(self):
        """Remove drawn lines/highlights without resetting the attempt counter."""
        self.pattern.clear()
        self.canvas.delete("pattern_line")
        self.canvas.delete("rubber_band")
        self.canvas.delete("message")
        # BUG 2 FIX: delete per-node highlight tags
        for n in self.nodes:
            self.canvas.delete(f"hl_{n}")
        self.status_label.config(text="Draw your pattern", fg="black")

    # ------------------------------------------------------------------
    # Button commands
    # ------------------------------------------------------------------

    def analyze_current_pattern(self):
        """Analyse the current pattern without running the access check."""
        if self.pattern:
            self.show_personality()
        else:
            self.insight_text.config(state=tk.NORMAL)
            self.insight_text.delete("1.0", tk.END)
            self.insight_text.insert("1.0", "Draw a pattern first!")
            self.insight_text.config(state=tk.DISABLED)

    def reset_pattern(self):
        """Clear the current drawing without affecting the attempt counter."""
        self._clear_drawn_pattern()

    def reset_all(self):
        """Full reset: clear drawing AND attempt counter."""
        self._clear_drawn_pattern()
        self.attempts = 0
        self.locked = False       # BUG 8 FIX: re-enable input after full reset
        self.attempts_label.config(
            text=f"Attempts: {self.attempts}/{self.max_attempts}")
        self.insight_text.config(state=tk.NORMAL)
        self.insight_text.delete("1.0", tk.END)
        self.insight_text.insert("1.0", "Your personality insight will appear here...")
        self.insight_text.config(state=tk.DISABLED)

    # ------------------------------------------------------------------
    # Setup
    # ------------------------------------------------------------------

    def setup_bindings(self):
        self.canvas.bind("<B1-Motion>",      self.drag)
        self.canvas.bind("<ButtonRelease-1>", self.release)
        self.canvas.bind("<Button-3>",        lambda e: self.reset_pattern())

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = PatternLock()
    app.run()