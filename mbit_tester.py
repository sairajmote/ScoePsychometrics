import numpy as np

class MBTI_Personality:
    def __init__(self):
        self.questions = None
        self.answers = np.zeros(98)
        self.meta = None
        self.dimension_scores = {}
        self.reliability = {}
        self.mbti_type = ""

    def initializeQuestions(self):
        self.questions = np.array([
            # ---- ORIGINAL 50 ----
            "I feel energized when I spend time with a lot of people.",
            "I focus on details and specifics when learning something new.",
            "I prioritize logic and objectivity when making decisions.",
            "I prefer to have a plan and stick to it.",
            "I find it easy to relate to people and understand their perspective.",
            "I prefer to reflect quietly by myself.",
            "I enjoy thinking about the future and the possibilities it holds.",
            "I consider people's feelings when making decisions.",
            "I am comfortable with changes and surprises.",
            "I enjoy solving complex problems and puzzles.",
            "I enjoy being the center of attention.",
            "I rely on my experiences when making decisions.",
            "I am straightforward and direct in my communication.",
            "I like to complete tasks well before the deadline.",
            "I prefer to focus on one task at a time.",
            "I often think before I speak.",
            "I trust my gut feelings and intuition.",
            "I try to be tactful and considerate in my communication.",
            "I often leave tasks until the last minute.",
            "I often find myself multi-tasking.",
            "I seek out social events and gatherings.",
            "I prefer clear and concrete information over abstract ideas.",
            "I value fairness and justice.",
            "I prefer structured environments with clear rules.",
            "I am drawn to artistic and creative activities.",
            "I need time alone to recharge after social interactions.",
            "I enjoy brainstorming and considering various ideas.",
            "I value empathy and compassion.",
            "I enjoy flexibility and spontaneity.",
            "I like to gather facts and data before making decisions.",
            "I like to talk through my problems.",
            "I am practical and down-to-earth.",
            "I enjoy analyzing problems and finding logical solutions.",
            "I like to keep my space organized and tidy.",
            "I like to think big picture rather than the details.",
            "I tend to keep my thoughts and feelings to myself.",
            "I often get lost in my own imagination.",
            "I am concerned with maintaining harmony in my relationships.",
            "I am adaptable and go with the flow.",
            "I am thorough and detail-oriented in my work.",
            "I prefer to work in teams rather than alone.",
            "I like to focus on what is happening right now.",
            "I am more likely to criticize than to compliment.",
            "I set goals and work systematically towards them.",
            "I prefer practical and hands-on activities.",
            "I enjoy deep, one-on-one conversations.",
            "I am drawn to concepts and theories.",
            "I often find myself putting others' needs ahead of my own.",
            "I prefer to keep my options open.",
            "I often contemplate the meaning and purpose of life.",

            # ---- 12 NEW SN ----
            "You focus more on facts than ideas.",
            "You enjoy imagining future possibilities.",
            "You rely on practical information.",
            "You enjoy abstract discussions.",
            "You prefer realistic solutions.",
            "You enjoy exploring theories.",
            "You trust past experiences.",
            "You like thinking about future innovations.",
            "You prefer concrete facts.",
            "You enjoy conceptual thinking.",
            "You trust facts over speculation.",
            "You enjoy philosophical thinking.",

            # ---- 12 NEW EI ----
            "You like meeting new people.",
            "You feel drained after social gatherings.",
            "You enjoy group activities.",
            "You like spending time alone.",
            "You start conversations easily.",
            "You prefer observing rather than participating in discussions.",
            "You enjoy networking events.",
            "You enjoy lively discussions.",
            "You prefer working independently.",
            "You feel energized around people.",
            "You need alone time to recharge.",
            "You enjoy being part of a crowd.",

            # ---- 12 NEW TF ----
            "You make decisions based on logic.",
            "You consider people's feelings when deciding.",
            "You value fairness over compassion.",
            "You analyze problems objectively.",
            "You prioritize truth over emotions.",
            "You try to avoid hurting people's feelings.",
            "You enjoy logical debates.",
            "You care deeply about others' emotions.",
            "You focus on objective reasoning.",
            "You value kindness in decisions.",
            "You trust logical conclusions.",
            "You trust emotional understanding.",

            # ---- 12 NEW JP ----
            "You prefer planning things in advance.",
            "You prefer being spontaneous.",
            "You like organized schedules.",
            "You prefer flexible plans.",
            "You complete tasks early.",
            "You enjoy adapting to sudden changes.",
            "You like structured routines.",
            "You prefer open-ended situations.",
            "You enjoy making detailed plans.",
            "You enjoy exploring without plans.",
            "You prefer clear deadlines.",
            "You prefer freedom in scheduling.",
        ])

        self.meta = np.array([
            # ---- ORIGINAL 50 ----
            ("EI", 1),  ("SN", 1),  ("TF", 1),  ("JP", 1),  ("TF", -1),
            ("EI", -1), ("SN", -1), ("TF", -1), ("JP", -1), ("TF", 1),
            ("EI", 1),  ("SN", 1),  ("TF", 1),  ("JP", 1),  ("JP", 1),
            ("EI", -1), ("SN", -1), ("TF", -1), ("JP", -1), ("JP", -1),
            ("EI", 1),  ("SN", 1),  ("TF", 1),  ("JP", 1),  ("SN", -1),
            ("EI", -1), ("SN", -1), ("TF", -1), ("JP", -1), ("SN", 1),
            ("EI", 1),  ("SN", 1),  ("TF", 1),  ("JP", 1),  ("SN", -1),
            ("EI", -1), ("SN", -1), ("TF", -1), ("JP", -1), ("SN", 1),
            ("EI", 1),  ("SN", 1),  ("TF", 1),  ("JP", 1),  ("SN", 1),
            ("EI", -1), ("SN", -1), ("TF", -1), ("JP", -1), ("SN", -1),

            # ---- 12 NEW SN ----
            ("SN", 1),  ("SN", -1), ("SN", 1),  ("SN", -1),
            ("SN", 1),  ("SN", -1), ("SN", 1),  ("SN", -1),
            ("SN", 1),  ("SN", -1), ("SN", 1),  ("SN", -1),

            # ---- 12 NEW EI ----
            ("EI", 1),  ("EI", -1), ("EI", 1),  ("EI", -1),
            ("EI", 1),  ("EI", -1), ("EI", 1),  ("EI", 1),
            ("EI", -1), ("EI", 1),  ("EI", -1), ("EI", 1),

            # ---- 12 NEW TF ----
            ("TF", 1),  ("TF", -1), ("TF", 1),  ("TF", 1),
            ("TF", 1),  ("TF", -1), ("TF", 1),  ("TF", -1),
            ("TF", 1),  ("TF", -1), ("TF", 1),  ("TF", -1),

            # ---- 12 NEW JP ----
            ("JP", 1),  ("JP", -1), ("JP", 1),  ("JP", -1),
            ("JP", 1),  ("JP", -1), ("JP", 1),  ("JP", -1),
            ("JP", 1),  ("JP", -1), ("JP", 1),  ("JP", -1),
        ], dtype=object)

    def takingTest(self):
        self.initializeQuestions()

        print("\n------- MBTI Personality Test (CTT) -------")
        print("Answer each question from 1 (Strongly Disagree) to 7 (Strongly Agree).")
        print("Type 'BREAK' to exit early.\n")

        answers = []
        for i, question in enumerate(self.questions):
            while True:
                raw = input(f"{i+1}. {question} ")
                if raw.upper() == "BREAK":
                    break
                try:
                    val = int(raw)
                    if 1 <= val <= 7:
                        answers.append(val)
                        break
                    else:
                        print("Please enter a number between 1 and 7.")
                except ValueError:
                    print("Invalid input.")
            if raw.upper() == "BREAK":
                break

        self.answers[:len(answers)] = answers
        self.analyzeResults(len(answers))

    def analyzeResults(self, n_answered):
        dimensions = ["EI", "SN", "TF", "JP"]
        first_letters = {"EI": "E", "SN": "S", "TF": "T", "JP": "J"}

        dim_items = {d: [] for d in dimensions}

        for i in range(n_answered):
            dim, direction = self.meta[i]
            raw = self.answers[i]
            direction = int(direction)
            scored = raw if direction == 1 else (8 - raw)
            dim_items[dim].append(scored)

        print("\n------- CTT Scores -------")
        mbti_result = ""

        for dim in dimensions:
            items = np.array(dim_items[dim])
            if len(items) == 0:
                continue

            mean_score = items.mean()
            alpha = self.cronbach_alpha(items)
            self.reliability[dim] = alpha

            midpoint = 4.0
            letter = first_letters[dim] if mean_score >= midpoint else dim[1]
            mbti_result += letter

            clarity_score = abs(mean_score - midpoint) / 3.0 * 100
            print(f"\n{dim}: mean={mean_score:.2f} | Cronbach's α={alpha:.2f} | Preference: {letter} ({clarity_score:.1f}% clarity)")

        self.mbti_type = mbti_result
        print(f"\n✅ Your MBTI Type: {self.mbti_type}")
        print("\n**This test is for self-exploration. Don't take it too literally!**")

    def cronbach_alpha(self, items):
        if len(items) < 2:
            return float('nan')

        k = len(items)
        item_vars = np.array([np.var([items[i]], ddof=1) if len(items) > 1 else 0 for i in range(k)])
        total_var = np.var(items, ddof=1)

        if total_var == 0:
            return float('nan')

        alpha = (k / (k - 1)) * (1 - item_vars.sum() / total_var)
        return float(np.clip(alpha, -1, 1))