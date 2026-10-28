import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

# Theme Colors
PRIMARY_DARK = RGBColor(15, 76, 129)     # Navy Blue (#0F4C81)
SECONDARY_LIGHT = RGBColor(224, 242, 254) # Sky Blue (#E0F2FE)
ACCENT_BLUE = RGBColor(37, 99, 235)      # Vivid Blue (#2563EB)
BG_COLOR = RGBColor(248, 250, 252)       # Soft Slate White (#F8FAFC)
TEXT_PRIMARY = RGBColor(31, 41, 55)      # Charcoal (#1F2937)
TEXT_MUTED = RGBColor(100, 116, 139)     # Gray (#64748B)
CODE_BG = RGBColor(15, 23, 42)           # Dark Slate (#0F172A)
WHITE = RGBColor(255, 255, 255)

class SlideBuilder:
    @staticmethod
    def set_background(slide, color):
        background = slide.background
        fill = background.fill
        fill.solid()
        fill.fore_color.rgb = color

    @staticmethod
    def add_slide_title(slide, text, color=PRIMARY_DARK):
        txBox = slide.shapes.add_textbox(Inches(0.75), Inches(0.4), Inches(11.833), Inches(0.8))
        tf = txBox.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
        p = tf.paragraphs[0]
        p.text = text
        p.font.name = 'Trebuchet MS'
        p.font.size = Pt(32)
        p.font.bold = True
        p.font.color.rgb = color
        
        if color == PRIMARY_DARK:
            # Underline shape
            line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.75), Inches(1.05), Inches(1.5), Inches(0.03))
            line.fill.solid()
            line.fill.fore_color.rgb = ACCENT_BLUE
            line.line.fill.background()

    @classmethod
    def create_title_slide(cls, prs, title, subtitle):
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        cls.set_background(slide, PRIMARY_DARK)
        
        # Decorative circular shapes
        shape1 = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(-1.5), Inches(-1.5), Inches(4.5), Inches(4.5))
        shape1.fill.solid()
        shape1.fill.fore_color.rgb = ACCENT_BLUE
        shape1.line.fill.background()
        
        shape2 = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(10.5), Inches(4.5), Inches(4.0), Inches(4.0))
        shape2.fill.solid()
        shape2.fill.fore_color.rgb = ACCENT_BLUE
        shape2.line.fill.background()
        
        # Title Box
        txBox = slide.shapes.add_textbox(Inches(1.0), Inches(2.2), Inches(11.333), Inches(2.2))
        tf = txBox.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
        
        p = tf.paragraphs[0]
        p.text = title
        p.font.name = 'Trebuchet MS'
        p.font.size = Pt(40)
        p.font.bold = True
        p.font.color.rgb = WHITE
        p.alignment = PP_ALIGN.CENTER
        
        p2 = tf.add_paragraph()
        p2.text = subtitle
        p2.font.name = 'Calibri'
        p2.font.size = Pt(18)
        p2.font.color.rgb = SECONDARY_LIGHT
        p2.alignment = PP_ALIGN.CENTER
        p2.space_before = Pt(20)
        
        # Footer
        txBox2 = slide.shapes.add_textbox(Inches(1.0), Inches(6.2), Inches(11.333), Inches(0.5))
        tf2 = txBox2.text_frame
        p3 = tf2.paragraphs[0]
        p3.text = "Complete Python Course | Video Tutorial Slide Deck"
        p3.font.name = 'Calibri'
        p3.font.size = Pt(12)
        p3.font.color.rgb = SECONDARY_LIGHT
        p3.alignment = PP_ALIGN.CENTER
        
        return slide

    @classmethod
    def create_content_slide(cls, prs, title, bullets, card_title=None, card_text=None):
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        cls.set_background(slide, BG_COLOR)
        cls.add_slide_title(slide, title)
        
        # Left Content Box (Bullets)
        left_width = Inches(7.5) if card_title else Inches(11.83)
        txBox = slide.shapes.add_textbox(Inches(0.75), Inches(1.5), left_width, Inches(5.0))
        tf = txBox.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
        
        for idx, bullet in enumerate(bullets):
            p = tf.add_paragraph() if idx > 0 else tf.paragraphs[0]
            p.text = bullet
            p.font.name = 'Calibri'
            p.font.size = Pt(18)
            p.font.color.rgb = TEXT_PRIMARY
            p.space_after = Pt(14)
            p.level = 0
            
        # Right Highlight Card
        if card_title and card_text:
            card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(8.75), Inches(1.5), Inches(3.833), Inches(5.0))
            card.fill.solid()
            card.fill.fore_color.rgb = SECONDARY_LIGHT
            card.line.color.rgb = ACCENT_BLUE
            card.line.width = Pt(1.5)
            
            tf_card = card.text_frame
            tf_card.word_wrap = True
            tf_card.margin_left = tf_card.margin_top = tf_card.margin_right = tf_card.margin_bottom = Inches(0.3)
            
            p_ct = tf_card.paragraphs[0]
            p_ct.text = card_title
            p_ct.font.name = 'Trebuchet MS'
            p_ct.font.size = Pt(18)
            p_ct.font.bold = True
            p_ct.font.color.rgb = PRIMARY_DARK
            p_ct.space_after = Pt(12)
            
            p_ctx = tf_card.add_paragraph()
            p_ctx.text = card_text
            p_ctx.font.name = 'Calibri'
            p_ctx.font.size = Pt(14)
            p_ctx.font.color.rgb = TEXT_PRIMARY
            p_ctx.space_after = Pt(8)
            
        return slide

    @classmethod
    def create_comparison_slide(cls, prs, title, col1_title, col1_bullets, col2_title, col2_bullets):
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        cls.set_background(slide, BG_COLOR)
        cls.add_slide_title(slide, title)
        
        # Column 1 Box
        card1 = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.75), Inches(1.5), Inches(5.6), Inches(5.0))
        card1.fill.solid()
        card1.fill.fore_color.rgb = WHITE
        card1.line.color.rgb = ACCENT_BLUE
        card1.line.width = Pt(1.5)
        
        tf1 = card1.text_frame
        tf1.word_wrap = True
        tf1.margin_left = tf1.margin_top = tf1.margin_right = tf1.margin_bottom = Inches(0.3)
        p1_title = tf1.paragraphs[0]
        p1_title.text = col1_title
        p1_title.font.name = 'Trebuchet MS'
        p1_title.font.size = Pt(18)
        p1_title.font.bold = True
        p1_title.font.color.rgb = PRIMARY_DARK
        p1_title.space_after = Pt(10)
        
        for bullet in col1_bullets:
            p = tf1.add_paragraph()
            p.font.name = 'Calibri'
            p.font.size = Pt(13)
            p.font.color.rgb = TEXT_PRIMARY
            p.space_after = Pt(4)
            
            if ":" in bullet:
                parts = bullet.split(":", 1)
                run_bold = p.add_run()
                run_bold.text = "• " + parts[0] + ":"
                run_bold.font.bold = True
                
                run_normal = p.add_run()
                run_normal.text = parts[1]
            else:
                run_normal = p.add_run()
                run_normal.text = "• " + bullet
            
        # Column 2 Box
        card2 = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.98), Inches(1.5), Inches(5.6), Inches(5.0))
        card2.fill.solid()
        card2.fill.fore_color.rgb = SECONDARY_LIGHT
        card2.line.color.rgb = ACCENT_BLUE
        card2.line.width = Pt(1.5)
        
        tf2 = card2.text_frame
        tf2.word_wrap = True
        tf2.margin_left = tf2.margin_top = tf2.margin_right = tf2.margin_bottom = Inches(0.3)
        p2_title = tf2.paragraphs[0]
        p2_title.text = col2_title
        p2_title.font.name = 'Trebuchet MS'
        p2_title.font.size = Pt(18)
        p2_title.font.bold = True
        p2_title.font.color.rgb = PRIMARY_DARK
        p2_title.space_after = Pt(10)
        
        for bullet in col2_bullets:
            p = tf2.add_paragraph()
            p.font.name = 'Calibri'
            p.font.size = Pt(13)
            p.font.color.rgb = TEXT_PRIMARY
            p.space_after = Pt(4)
            
            if ":" in bullet:
                parts = bullet.split(":", 1)
                run_bold = p.add_run()
                run_bold.text = "• " + parts[0] + ":"
                run_bold.font.bold = True
                
                run_normal = p.add_run()
                run_normal.text = parts[1]
            else:
                run_normal = p.add_run()
                run_normal.text = "• " + bullet
            
        return slide

    @classmethod
    def create_code_slide(cls, prs, title, code, output, explanation_bullets):
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        cls.set_background(slide, BG_COLOR)
        cls.add_slide_title(slide, title)
        
        # Code Box
        editor = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.75), Inches(1.5), Inches(6.5), Inches(3.2))
        editor.fill.solid()
        editor.fill.fore_color.rgb = CODE_BG
        editor.line.color.rgb = ACCENT_BLUE
        editor.line.width = Pt(1.5)
        
        tf_code = editor.text_frame
        tf_code.word_wrap = True
        tf_code.margin_left = tf_code.margin_top = tf_code.margin_right = tf_code.margin_bottom = Inches(0.2)
        
        p_c = tf_code.paragraphs[0]
        p_c.text = "# Source Python Code\n" + code
        p_c.font.name = 'Consolas'
        p_c.font.size = Pt(12)
        p_c.font.color.rgb = WHITE
        
        # Terminal Output Box
        terminal = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.75), Inches(4.9), Inches(6.5), Inches(1.6))
        terminal.fill.solid()
        terminal.fill.fore_color.rgb = TEXT_PRIMARY
        terminal.line.color.rgb = TEXT_MUTED
        
        tf_term = terminal.text_frame
        tf_term.word_wrap = True
        tf_term.margin_left = tf_term.margin_top = tf_term.margin_right = tf_term.margin_bottom = Inches(0.15)
        
        p_t = tf_term.paragraphs[0]
        p_t.text = ">>> OUTPUT:\n" + output
        p_t.font.name = 'Consolas'
        p_t.font.size = Pt(11)
        p_t.font.color.rgb = SECONDARY_LIGHT
        
        # Right explanation panel
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(7.5), Inches(1.5), Inches(5.083), Inches(5.0))
        card.fill.solid()
        card.fill.fore_color.rgb = SECONDARY_LIGHT
        card.line.color.rgb = ACCENT_BLUE
        
        tf_card = card.text_frame
        tf_card.word_wrap = True
        tf_card.margin_left = tf_card.margin_top = tf_card.margin_right = tf_card.margin_bottom = Inches(0.3)
        
        p_card_title = tf_card.paragraphs[0]
        p_card_title.text = "Program Execution Trace"
        p_card_title.font.name = 'Trebuchet MS'
        p_card_title.font.size = Pt(18)
        p_card_title.font.bold = True
        p_card_title.font.color.rgb = PRIMARY_DARK
        p_card_title.space_after = Pt(12)
        
        for bullet in explanation_bullets:
            p = tf_card.add_paragraph()
            p.text = "• " + bullet
            p.font.name = 'Calibri'
            p.font.size = Pt(14)
            p.font.color.rgb = TEXT_PRIMARY
            p.space_after = Pt(6)
            
        return slide

    @classmethod
    def create_diagram_slide(cls, prs, title, diagram_type, steps):
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        cls.set_background(slide, BG_COLOR)
        cls.add_slide_title(slide, title)
        
        shapes = slide.shapes
        num_steps = min(len(steps), 4)
        box_width = Inches(2.4)
        box_height = Inches(1.5)
        spacing = Inches(0.6)
        start_x = Inches(0.75)
        y = Inches(3.0)
        
        for idx in range(num_steps):
            x = start_x + idx * (box_width + spacing)
            
            shape_type = MSO_SHAPE.ROUNDED_RECTANGLE
            if idx == 0:
                shape_type = MSO_SHAPE.OVAL
            elif idx == num_steps - 1:
                shape_type = MSO_SHAPE.OVAL
            elif idx == 1 and diagram_type == 'decision':
                shape_type = MSO_SHAPE.DIAMOND
                
            box = shapes.add_shape(shape_type, x, y, box_width, box_height)
            box.fill.solid()
            if idx % 2 == 0:
                box.fill.fore_color.rgb = PRIMARY_DARK
                text_color = WHITE
            else:
                box.fill.fore_color.rgb = SECONDARY_LIGHT
                text_color = PRIMARY_DARK
                
            box.line.color.rgb = ACCENT_BLUE
            box.line.width = Pt(1.5)
            
            tf = box.text_frame
            tf.word_wrap = True
            tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = Inches(0.1)
            
            p = tf.paragraphs[0]
            p.text = steps[idx]
            p.font.name = 'Calibri'
            p.font.size = Pt(13)
            p.font.bold = True
            p.font.color.rgb = text_color
            p.alignment = PP_ALIGN.CENTER
            
            # Draw linking arrow
            if idx < num_steps - 1:
                arrow_x = x + box_width + Inches(0.1)
                arrow = shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, arrow_x, y + Inches(0.5), spacing - Inches(0.2), Inches(0.5))
                arrow.fill.solid()
                arrow.fill.fore_color.rgb = ACCENT_BLUE
                arrow.line.fill.background()
                
        return slide

    @classmethod
    def create_interview_question_slide(cls, prs, title, question, q_num):
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        cls.set_background(slide, BG_COLOR)
        cls.add_slide_title(slide, f"Interview Preparation - Question {q_num}")
        
        # Left Card (Question)
        q_card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.75), Inches(1.5), Inches(5.6), Inches(5.0))
        q_card.fill.solid()
        q_card.fill.fore_color.rgb = PRIMARY_DARK
        q_card.line.color.rgb = ACCENT_BLUE
        
        tf_q = q_card.text_frame
        tf_q.word_wrap = True
        tf_q.margin_left = tf_q.margin_top = tf_q.margin_right = tf_q.margin_bottom = Inches(0.4)
        
        p_q_lbl = tf_q.paragraphs[0]
        p_q_lbl.text = "TECHNICAL INTERVIEW QUESTION"
        p_q_lbl.font.name = 'Trebuchet MS'
        p_q_lbl.font.size = Pt(14)
        p_q_lbl.font.bold = True
        p_q_lbl.font.color.rgb = SECONDARY_LIGHT
        p_q_lbl.space_after = Pt(15)
        
        p_q = tf_q.add_paragraph()
        p_q.text = question
        p_q.font.name = 'Calibri'
        p_q.font.size = Pt(22)
        p_q.font.bold = True
        p_q.font.color.rgb = WHITE
        
        # Right Card (Click to Reveal Button)
        btn_card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.98), Inches(1.5), Inches(5.6), Inches(5.0))
        btn_card.fill.solid()
        btn_card.fill.fore_color.rgb = SECONDARY_LIGHT
        btn_card.line.color.rgb = ACCENT_BLUE
        btn_card.line.width = Pt(2.0)
        
        tf_btn = btn_card.text_frame
        tf_btn.word_wrap = True
        
        p_btn = tf_btn.paragraphs[0]
        p_btn.text = "\n\n\n\n👉 CLICK TO REVEAL ANSWER\n[Click / Spacebar]"
        p_btn.font.name = 'Trebuchet MS'
        p_btn.font.size = Pt(20)
        p_btn.font.bold = True
        p_btn.font.color.rgb = ACCENT_BLUE
        p_btn.alignment = PP_ALIGN.CENTER
        
        return slide

    @classmethod
    def create_interview_answer_slide(cls, prs, title, question, answer, q_num):
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        cls.set_background(slide, BG_COLOR)
        cls.add_slide_title(slide, f"Interview Preparation - Answer {q_num}")
        
        # Left Card (Question)
        q_card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.75), Inches(1.5), Inches(5.6), Inches(5.0))
        q_card.fill.solid()
        q_card.fill.fore_color.rgb = PRIMARY_DARK
        q_card.line.color.rgb = ACCENT_BLUE
        
        tf_q = q_card.text_frame
        tf_q.word_wrap = True
        tf_q.margin_left = tf_q.margin_top = tf_q.margin_right = tf_q.margin_bottom = Inches(0.4)
        
        p_q_lbl = tf_q.paragraphs[0]
        p_q_lbl.text = "TECHNICAL INTERVIEW QUESTION"
        p_q_lbl.font.name = 'Trebuchet MS'
        p_q_lbl.font.size = Pt(14)
        p_q_lbl.font.bold = True
        p_q_lbl.font.color.rgb = SECONDARY_LIGHT
        p_q_lbl.space_after = Pt(15)
        
        p_q = tf_q.add_paragraph()
        p_q.text = question
        p_q.font.name = 'Calibri'
        p_q.font.size = Pt(22)
        p_q.font.bold = True
        p_q.font.color.rgb = WHITE
        
        # Right Card (Answer Revealed)
        ans_card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.98), Inches(1.5), Inches(5.6), Inches(5.0))
        ans_card.fill.solid()
        ans_card.fill.fore_color.rgb = WHITE
        ans_card.line.color.rgb = ACCENT_BLUE
        ans_card.line.width = Pt(1.5)
        
        tf_ans = ans_card.text_frame
        tf_ans.word_wrap = True
        tf_ans.margin_left = tf_ans.margin_top = tf_ans.margin_right = tf_ans.margin_bottom = Inches(0.3)
        
        p_ans_lbl = tf_ans.paragraphs[0]
        p_ans_lbl.text = "IDEAL RESPONSE"
        p_ans_lbl.font.name = 'Trebuchet MS'
        p_ans_lbl.font.size = Pt(16)
        p_ans_lbl.font.bold = True
        p_ans_lbl.font.color.rgb = ACCENT_BLUE
        p_ans_lbl.space_after = Pt(15)
        
        p_ans = tf_ans.add_paragraph()
        p_ans.text = answer
        p_ans.font.name = 'Calibri'
        p_ans.font.size = Pt(15)
        p_ans.font.color.rgb = TEXT_PRIMARY
        
        return slide

    @classmethod
    def create_quiz_question_slide(cls, prs, title, question, options):
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        cls.set_background(slide, BG_COLOR)
        cls.add_slide_title(slide, "Interactive Concept Quiz")
        
        # Question card (Left)
        q_card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.75), Inches(1.5), Inches(5.6), Inches(5.0))
        q_card.fill.solid()
        q_card.fill.fore_color.rgb = PRIMARY_DARK
        q_card.line.color.rgb = ACCENT_BLUE
        
        tf_q = q_card.text_frame
        tf_q.word_wrap = True
        tf_q.margin_left = tf_q.margin_top = tf_q.margin_right = tf_q.margin_bottom = Inches(0.4)
        
        p_q_lbl = tf_q.paragraphs[0]
        p_q_lbl.text = "CONCEPT CHECK"
        p_q_lbl.font.name = 'Trebuchet MS'
        p_q_lbl.font.size = Pt(16)
        p_q_lbl.font.bold = True
        p_q_lbl.font.color.rgb = SECONDARY_LIGHT
        p_q_lbl.space_after = Pt(15)
        
        p_q = tf_q.add_paragraph()
        p_q.text = question
        p_q.font.name = 'Calibri'
        p_q.font.size = Pt(20)
        p_q.font.bold = True
        p_q.font.color.rgb = WHITE
        
        # Options cards (Right - all colored default sky blue)
        for idx, option in enumerate(options):
            y_offset = Inches(1.5) + idx * Inches(1.2)
            opt_card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.98), y_offset, Inches(5.6), Inches(1.0))
            opt_card.fill.solid()
            opt_card.fill.fore_color.rgb = SECONDARY_LIGHT
            opt_card.line.color.rgb = ACCENT_BLUE
            opt_card.line.width = Pt(1.5)
            
            tf_opt = opt_card.text_frame
            tf_opt.word_wrap = True
            tf_opt.margin_left = tf_opt.margin_top = tf_opt.margin_right = tf_opt.margin_bottom = Inches(0.15)
            
            p_opt = tf_opt.paragraphs[0]
            prefix = ["A", "B", "C", "D"][idx]
            p_opt.text = f"{prefix}. {option}"
            p_opt.font.name = 'Calibri'
            p_opt.font.size = Pt(15)
            p_opt.font.color.rgb = TEXT_PRIMARY
            
        return slide

    @classmethod
    def create_quiz_answer_slide(cls, prs, title, question, options, correct_answer, explanation):
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        cls.set_background(slide, BG_COLOR)
        cls.add_slide_title(slide, "Quiz - Correct Answer")
        
        # Question card (Left)
        q_card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.75), Inches(1.5), Inches(5.6), Inches(5.0))
        q_card.fill.solid()
        q_card.fill.fore_color.rgb = PRIMARY_DARK
        q_card.line.color.rgb = ACCENT_BLUE
        
        tf_q = q_card.text_frame
        tf_q.word_wrap = True
        tf_q.margin_left = tf_q.margin_top = tf_q.margin_right = tf_q.margin_bottom = Inches(0.3)
        
        p_q_lbl = tf_q.paragraphs[0]
        p_q_lbl.text = "CONCEPT CHECK"
        p_q_lbl.font.name = 'Trebuchet MS'
        p_q_lbl.font.size = Pt(16)
        p_q_lbl.font.bold = True
        p_q_lbl.font.color.rgb = SECONDARY_LIGHT
        p_q_lbl.space_after = Pt(15)
        
        p_q = tf_q.add_paragraph()
        p_q.text = question
        p_q.font.name = 'Calibri'
        p_q.font.size = Pt(18)
        p_q.font.bold = True
        p_q.font.color.rgb = WHITE
        
        # Explanations addition inside the left card
        p_exp_lbl = tf_q.add_paragraph()
        p_exp_lbl.text = "\nEXPLANATION:"
        p_exp_lbl.font.name = 'Trebuchet MS'
        p_exp_lbl.font.size = Pt(12)
        p_exp_lbl.font.bold = True
        p_exp_lbl.font.color.rgb = SECONDARY_LIGHT
        
        p_exp = tf_q.add_paragraph()
        p_exp.text = explanation
        p_exp.font.name = 'Calibri'
        p_exp.font.size = Pt(13)
        p_exp.font.color.rgb = WHITE
        
        # Options cards (Right - correct highlighted in white with bold border)
        for idx, option in enumerate(options):
            y_offset = Inches(1.5) + idx * Inches(1.2)
            opt_card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.98), y_offset, Inches(5.6), Inches(1.0))
            opt_card.fill.solid()
            opt_card.fill.fore_color.rgb = WHITE if option == correct_answer else SECONDARY_LIGHT
            opt_card.line.color.rgb = ACCENT_BLUE if option == correct_answer else TEXT_MUTED
            opt_card.line.width = Pt(2.0) if option == correct_answer else Pt(1.0)
            
            tf_opt = opt_card.text_frame
            tf_opt.word_wrap = True
            tf_opt.margin_left = tf_opt.margin_top = tf_opt.margin_right = tf_opt.margin_bottom = Inches(0.15)
            
            p_opt = tf_opt.paragraphs[0]
            prefix = ["A", "B", "C", "D"][idx]
            p_opt.text = f"{prefix}. {option}" + (" ✓ (Correct)" if option == correct_answer else "")
            p_opt.font.name = 'Calibri'
            p_opt.font.size = Pt(15)
            p_opt.font.color.rgb = ACCENT_BLUE if option == correct_answer else TEXT_PRIMARY
            if option == correct_answer:
                p_opt.font.bold = True
                
        return slide

    @classmethod
    def create_summary_slide(cls, prs, title, summary_points, references):
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        cls.set_background(slide, BG_COLOR)
        cls.add_slide_title(slide, title)
        
        # Left summary box
        card1 = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.75), Inches(1.5), Inches(5.6), Inches(5.0))
        card1.fill.solid()
        card1.fill.fore_color.rgb = WHITE
        card1.line.color.rgb = ACCENT_BLUE
        card1.line.width = Pt(1.5)
        
        tf1 = card1.text_frame
        tf1.word_wrap = True
        tf1.margin_left = tf1.margin_top = tf1.margin_right = tf1.margin_bottom = Inches(0.3)
        p1_title = tf1.paragraphs[0]
        p1_title.text = "Topic Recap"
        p1_title.font.name = 'Trebuchet MS'
        p1_title.font.size = Pt(20)
        p1_title.font.bold = True
        p1_title.font.color.rgb = PRIMARY_DARK
        p1_title.space_after = Pt(10)
        
        for bullet in summary_points:
            p = tf1.add_paragraph()
            p.text = "✓ " + bullet
            p.font.name = 'Calibri'
            p.font.size = Pt(14)
            p.font.color.rgb = TEXT_PRIMARY
            p.space_after = Pt(8)
            
        # Right references box
        card2 = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.98), Inches(1.5), Inches(5.6), Inches(5.0))
        card2.fill.solid()
        card2.fill.fore_color.rgb = SECONDARY_LIGHT
        card2.line.color.rgb = ACCENT_BLUE
        card2.line.width = Pt(1.5)
        
        tf2 = card2.text_frame
        tf2.word_wrap = True
        tf2.margin_left = tf2.margin_top = tf2.margin_right = tf2.margin_bottom = Inches(0.3)
        p2_title = tf2.paragraphs[0]
        p2_title.text = "Recommended Resources"
        p2_title.font.name = 'Trebuchet MS'
        p2_title.font.size = Pt(20)
        p2_title.font.bold = True
        p2_title.font.color.rgb = PRIMARY_DARK
        p2_title.space_after = Pt(10)
        
        for ref in references:
            p = tf2.add_paragraph()
            p.text = "🔗 " + ref
            p.font.name = 'Calibri'
            p.font.size = Pt(13)
            p.font.color.rgb = TEXT_PRIMARY
            p.space_after = Pt(10)
            
        return slide

    @classmethod
    def create_table_slide(cls, prs, title, headers, rows):
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        cls.set_background(slide, BG_COLOR)
        cls.add_slide_title(slide, title)
        
        # Position table on slide
        left = Inches(0.66)
        top = Inches(1.5)
        width = Inches(12.0)
        height = Inches(5.0)
        
        table_shape = slide.shapes.add_table(len(rows) + 1, len(headers), left, top, width, height)
        table = table_shape.table
        
        # Column widths
        if len(headers) == 3:
            table.columns[0].width = Inches(2.2)
            table.columns[1].width = Inches(4.9)
            table.columns[2].width = Inches(4.9)
            
        # Style headers
        for col_idx, header in enumerate(headers):
            cell = table.cell(0, col_idx)
            cell.text = header
            cell.fill.solid()
            cell.fill.fore_color.rgb = PRIMARY_DARK
            
            p = cell.text_frame.paragraphs[0]
            p.font.name = 'Trebuchet MS'
            p.font.size = Pt(13)
            p.font.bold = True
            p.font.color.rgb = WHITE
            p.alignment = PP_ALIGN.CENTER
            
        # Style rows with alternating backgrounds
        for row_idx, row_data in enumerate(rows):
            for col_idx, cell_value in enumerate(row_data):
                cell = table.cell(row_idx + 1, col_idx)
                cell.text = cell_value
                cell.fill.solid()
                if (row_idx + 1) % 2 == 0:
                    cell.fill.fore_color.rgb = SECONDARY_LIGHT
                else:
                    cell.fill.fore_color.rgb = WHITE
                    
                p = cell.text_frame.paragraphs[0]
                p.font.name = 'Calibri'
                p.font.size = Pt(11)
                p.font.color.rgb = TEXT_PRIMARY
                if col_idx == 0:
                    p.font.bold = True
                    p.font.color.rgb = PRIMARY_DARK
                    p.alignment = PP_ALIGN.CENTER
                else:
                    p.alignment = PP_ALIGN.LEFT
                    
        return slide

def generate_speaker_notes(ppt_title, slide_title, slide_type, details):
    notes_intro = f"Hello everyone, welcome to today's video on {ppt_title}. We will examine the slide topic, which is {slide_title}. This topic is a core component of your Python programming journey, and understanding it is crucial for writing efficient and debuggable Python code."
    
    if slide_type == 'title':
        notes_body = f"This presentation deck represents a complete tutorial covering {ppt_title} as defined in our course curriculum. We will study the standard definition, detailed features, syntax structures, coding implementations with console outputs, common errors, and best practices. There are also practice questions, interview preparations, and a quiz at the end."
    elif slide_type == 'objectives':
        notes_body = f"On this slide, we outline our learning goals for this video. By the end of this tutorial, you will understand the basic syntax conventions, the execution flow within the interpreter, and how this feature integrates into larger structural components of the language. We will write multiple small code programs during this session to demonstrate these concepts live."
    elif slide_type == 'concepts':
        notes_body = f"Let's focus on the primary concepts. Logically, we define this structure as {details.get('definition', 'a fundamental construct in computing')}. Its core features include {', '.join(details.get('features', ['clean syntax', 'compiler directives'])[:3])}. Understanding the internal evaluation is vital for passing your coding interviews and technical evaluations."
    elif slide_type == 'advantages':
        notes_body = f"Let's review the main advantages. Using this construct provides benefits like {', '.join(details.get('advantages', ['easier coding', 'modular structure'])[:3])}. However, there are limitations to keep in mind, specifically {', '.join(details.get('disadvantages', ['runtime overhead', 'dynamic naming complexities'])[:2])}. Knowing these limitations helps us write better code."
    elif slide_type == 'syntax':
        notes_body = f"Here is the standard syntax. Notice how the keyword is placed at the start, followed by appropriate parameters and concluding with a colon. Since Python uses indentation to represent execution blocks rather than curly braces, you must be extremely consistent with your spacing. In your code, always use 4 spaces for cleaner structure."
    elif slide_type == 'code':
        notes_body = f"Now, let's analyze the code implementation. Look at the slate-colored code editor box on the left. We declare our variables and use the structure. When we execute this script, the PVM runs it line-by-line and generates the output shown in the terminal console box. Notice how the logic handles basic and edge cases without runtime errors."
    elif slide_type == 'mistakes':
        notes_body = f"In coding exercises, learners often make mistakes such as {', '.join(details.get('mistakes', ['indentation syntax error', 'scope variable errors'])[:2])}. To prevent this, implement the best practices on the right. Keep names descriptive, write simple modular lines, and insert docstrings for documentation. This ensures your script is maintainable."
    elif slide_type == 'applications':
        notes_body = f"In industry, these principles are used to design solid applications. For example, {', '.join(details.get('applications', ['automation script engines', 'system utilities'])[:2])} rely heavily on these mechanisms. As Python learners, practicing these logic flows will build the technical foundation needed for coding interviews and software engineering jobs."
    elif slide_type == 'interview_q':
        notes_body = f"Let's read this interview question: '{details.get('interview_q', 'How do you implement this concept?')}' Take a moment to think about this logically. How would you explain the underlying memory model or syntax execution to a technical interviewer? On the next click, we will reveal the ideal answer."
    elif slide_type == 'interview_a':
        notes_body = f"Now, as you can see, the ideal answer is revealed. When answering this question in an interview round, you must cover the core definition first, then write a simple code syntax block, and explain the runtime performance. This shows the interviewer you have both theoretical and coding skills."
    elif slide_type == 'quiz_q':
        notes_body = f"It's time for a quick quiz. Let's check our understanding. Read the question carefully: '{details.get('quiz_q', 'What is the default behavior?')}' Think about how Python evaluates this. Take a moment to pick your choice. On the next click, we will reveal the correct option."
    elif slide_type == 'quiz_a':
        notes_body = f"The correct option is highlighted on the right. Notice why the other choices fail; they either violate interpreter rules or type rules. This is a very common interview question, so make sure you note down this reasoning for your records."
    else:
        notes_body = f"To summarize today's video on {ppt_title}, we studied the basic definitions, operations, advantages, and syntax rules. Please refer to the textbook references and official documentation links provided on the slide for further reading. Make sure to complete the practice exercises before your next coding session."

    notes_conclusion = "Are there any questions on these concepts before we proceed to the live demonstration in our Python interpreter shell?"
    
    full_notes = f"{notes_intro} {notes_body} {notes_conclusion}"
    words = full_notes.split()
    
    if len(words) < 140:
        pad = " Please note that programming proficiency is only built through active coding and consistent debugging in your IDE. Pay close attention to indentation structures and error tracebacks in your editor."
        words.extend(pad.split())
    if len(words) > 180:
        words = words[:170]
        
    return " ".join(words)

# Predefined outline data list
COURSE_DATA = []

# Predefined outline topics mapped exactly to the 30 presentation decks
SYLLABUS_TOPICS = [
    # UNIT 1
    (1, "Introduction to Python and Features", "01_Python_Introduction_and_Features.pptx", 
     "High-level, interpreted, dynamically typed language features", 
     "Python is a general-purpose, interpreted, dynamically typed language created by Guido van Rossum in 1889, emphasizing high readability and developer productivity.", 
     ["Interpreted Execution Model: Code executes line-by-line via the Python Virtual Machine (PVM).",
      "Dynamic Typing: Variables do not require explicit type declaration before assignment.",
      "Automatic Memory Management: Features built-in garbage collection for unreferenced objects.",
      "High Readability: Uses indentation blocks rather than brackets or curly braces to define scope."],
     ["Extremely rapid prototyping and scripting speeds.", "Cross-platform support across Windows, macOS, Linux.", "Automatic memory allocation handles memory leaks."],
     ["Execution speed is slower than compiled languages like C or C++.", "Type safety errors only appear at runtime, not compile time."],
     ["No variable type declaration needed.", "Indentation (4 spaces) is syntax-enforced.", "Case-sensitive keywords and names."],
     "x = 5\n# Dynamic assignment:\nx = 'Hello'",
     ["Interpreter processes source code", "Parser builds abstract syntax tree", "Compiler generates bytecode (.pyc)", "PVM executes bytecode line-by-line"],
     "x = 5\nprint(type(x))\nx = 'Python'\nprint(type(x))",
     "<class 'int'>\n<class 'str'>",
     ["Declares variable x as an integer", "Prints class type of x", "Reassigns x to point to a string", "Prints new class type of x"],
     "a = 10\nb = 20\na, b = b, a\nprint('a:', a, 'b:', b)",
     "a: 20 b: 10",
     ["Initializes variables a and b", "Performs tuple unpacking to swap values in a single line", "Outputs the swapped variables"],
     ["Confusing indentation blocks", "Assuming compiled variables speed"],
     ["Write clean PEP 8 compliant script layouts", "Use linters to check structure"],
     ["System scripting automation", "Web servers logic routing", "Data pipeline scripting tools"],
     "What is the difference between compiler and interpreter execution models?",
     "A compiler translates the entire source program into machine code files at once. An interpreter translates and executes source code line-by-line at runtime, which simplifies debugging.",
     "Why is Python considered dynamically typed?",
     "Because type checking occurs at runtime. A variable is simply a pointer; you can reassign it to point to objects of different classes without errors.",
     "Write a script that Swaps two numbers in a single statement without using a temporary variable.",
     "Show how variable values reference objects in memory using the id() method.",
     "Which of the following describes Python's execution model?",
     ["Source code is compiled directly to machine binary", "Bytecode is generated and executed by PVM at runtime", "Executable file is linked statically before execution", "Hardware execution occurs without interpretation"],
     "Bytecode is generated and executed by PVM at runtime",
     "Python compiles source files to bytecode first, which is then dynamically interpreted by the PVM (Python Virtual Machine) during program execution.",
     ["Python features high readability.", "Dynamic typing speeds up scripting.", "PVM executes code line-by-line."]),

    (2, "Python IDEs and Execution Model", "02_Python_IDEs_and_Execution.pptx",
     "Development environments and internal compilation steps",
     "Integrated Development Environments (IDEs) combine code editing, debugging, execution, and autocomplete features into one workspace.",
     ["Code editor highlights syntax keywords dynamically.",
      "Integrated debugger allows setting breakpoints to inspect states.",
      "Interactive shell runs micro-statements for testing.",
      "Built-in console outputs standard streams (stdout/stderr)."],
     ["Speeds up development through syntax coloring and code completion.", "Integrated tools allow quick testing in terminal consoles."],
     ["IDEs use significant system RAM and hardware resources.", "Configuring paths and interpreters can confuse beginners."],
     ["Select correct interpreter path in editor settings.", "Install dependencies inside virtual environments.", "Run code using IDE execute shortcuts."],
     "# Launch program inside terminal\npython script.py",
     ["Editor compiles code to bytecode", "Writes compilation to __pycache__ directory", "PVM loads compiled instructions", "PVM processes input/output streams"],
     "import sys\nprint('Executable:', sys.executable)\nprint('Version:', sys.version[:5])",
     "Executable: C:\\Python\\python.exe\nVersion: 3.10",
     ["Imports the standard sys utility module", "Prints absolute path to active python executable", "Prints main version numbers"],
     "a = 5\nb = 10\nassert a * b == 50\nprint('Assert Passed!')",
     "Assert Passed!",
     ["Assigns operands a and b", "Uses assert keyword to validate logic", "Prints pass confirmation to console"],
     ["Running scripts with wrong python path", "Ignoring syntax errors shown in editor gutter"],
     ["Always code inside virtual environments", "Utilize code formatters like black or autopep8"],
     ["Local script debug environments", "Standardized developer workspaces", "Fast automated testing environments"],
     "What is bytecode and where is it stored?",
     "Bytecode is a platform-independent instruction set. It is stored inside local __pycache__ folders as .pyc files for execution efficiency.",
     "Explain the role of the PVM (Python Virtual Machine).",
     "The PVM is the runtime engine that loads bytecode, translates it into system machine instructions, and runs it on the CPU.",
     "Install PyCharm or VS Code and write a basic configuration script.",
     "Demonstrate setting a code breakpoint in your IDE to trace variables.",
     "Which folder contains compiled bytecode files?",
     ["__pycache__", "bin", "include", "libs"],
     "__pycache__",
     "The __pycache__ directory contains the compiled bytecode (.pyc files) generated by Python to speed up script load times.",
     ["IDEs integrate tools for faster developer flow.", "Source code compiles to bytecode .pyc files.", "PVM interpretations execute the bytecode."]),

    (3, "Comments and Identifiers", "03_Comments_and_Identifiers.pptx",
     "Code documentation rules and entity naming conventions",
     "Comments are notes that the interpreter ignores. Identifiers are names given to variables, functions, classes, and modules.",
     ["Single-line comments are declared using the hash symbol (#).",
      "Multi-line comments are written using triple quotes (''' or \"\"\").",
      "Identifiers must begin with a letter or underscore, not numbers.",
      "Identifiers are case-sensitive; tax, Tax, and TAX are unique."],
     ["Comments explain complex logic, easing code maintenance.", "Proper identifier naming creates self-documenting code bases."],
     ["Outdated comments confuse developers if code changes.", "Long identifier names can make expressions wordy."],
     ["Use # for inline explanations.", "Triple quotes at function starts create docstrings.", "Identifiers cannot use keywords or symbols."],
     "x = 5  # Inline comment\n'''\nMulti-line comment block\n'''",
     ["Interpreter parses syntax tokens", "Filters out comments and docstrings", "Maps identifier labels to memory references", "Resolves namespace references"],
     "def add_vals(x, y):\n    '''Returns sum of inputs.'''\n    return x + y\nprint(add_vals.__doc__)\nprint(add_vals(3, 4))",
     "Returns sum of inputs.\n7",
     ["Declares function with descriptive identifier name", "Defines triple-quote docstring documentation", "Prints docstring attribute and sum result"],
     "tax_rate = 0.18\nTax_Rate = 0.20\nprint('tax:', tax_rate, 'Tax:', Tax_Rate)",
     "tax: 0.18 Tax: 0.2",
     ["Declares two variables with different casing", "Demonstrates that case sensitivity separates identifiers", "Prints both distinct values"],
     ["Starting identifiers with numbers", "Using hyphens or spaces in variable names"],
     ["Follow snake_case for variable and function names", "Write concise comments explaining why, not what"],
     ["Code documentation generation", "API documentation hosting", "Large codebase refactoring structures"],
     "What are the syntax rules for declaring valid identifiers?",
     "Identifiers must start with an English letter or an underscore. The remaining characters can be letters, underscores, or digits. No spaces or special characters are allowed.",
     "How do docstrings differ from standard comments?",
     "Comments are discarded during compilation. Docstrings are compiled into the code object and can be queried dynamically via the __doc__ attribute.",
     "Write a function and extract its docstring dynamically in the print console.",
     "Find all invalid identifiers in a given list of variable names.",
     "Which of the following is a valid identifier name in Python?",
     ["2_count", "total-amount", "total_amount", "def"],
     "total_amount",
     "Identifiers cannot start with numbers, contain hyphens, or use reserved Python keywords like 'def'. Only letters, digits, and underscores are allowed.",
     ["Comments docstring explain logic rules.", "Identifiers naming rules are strictly enforced.", "Namespace registers case-sensitive names."]),

    (4, "Variables and Assignment", "04_Variables_and_Assignment.pptx",
     "Variable declarations, values referencing, and assignment operators",
     "Variables are named references that point to objects created in computer memory, using dynamic typing principles.",
     ["Assignment operator (=) links variable name to object in memory.",
      "Multiple variable assignments can be declared in a single line.",
      "Variables are pointers to objects, not fixed memory slots.",
      "Variables are destroyed automatically via garbage collection."],
     ["Dynamic typing eliminates variable type conversions.", "Swapping values in a single statement reduces boilerplate."],
     ["No compile-time type checking raises runtime errors.", "Shared memory references can cause unexpected side-effects."],
     ["Write name on left and value on right of equal sign.", "Performs dynamic object reassignment automatically.", "Avoid reserved keywords for variable names."],
     "a = 5\nx, y = 10, 'Data'",
     ["Evaluates expression on the right first", "Creates object in heap memory with value", "Binds identifier name to the heap reference", "Increments object reference counter"],
     "x = [1, 2]\ny = x\ny.append(3)\nprint('x:', x, 'y:', y)",
     "x: [1, 2, 3] y: [1, 2, 3]",
     ["Declares x pointing to a mutable list in memory", "Binds y to the exact same list address", "Modifies list via y, showing x changes too"],
     "a = 10\nb = 20\na, b = b, a\nprint('a:', a, 'b:', b)",
     "a: 20 b: 10",
     ["Assigns values 10 and 20 to a and b", "Performs tuple unpacking to swap values simultaneously", "Prints the swapped values"],
     ["Reassigning variables incorrectly inside functions", "Confusing variable reference copies with object copies"],
     ["Keep variable names lowercase with underscores", "Do not create multiple references to mutable objects unexpectedly"],
     ["Dynamic memory management", "Variable tracking in applications", "State tracking in loop structures"],
     "What does it mean that variables are pointers in Python?",
     "Unlike C/C++ where variables are named slots in memory, Python variables are names bound to objects stored on the heap.",
     "How does garbage collection track unreferenced variables?",
     "By reference counting. When an object's reference count drops to zero (no variables point to it), it is cleaned from memory.",
     "Show how to assign one value to three variables simultaneously.",
     "Print the memory address of a variable using the id() function.",
     "What happens to the object in memory when a variable is reassigned?",
     ["The object value is changed immediately", "The old object is deleted and replaced", "The variable points to the new object", "The program raises a type error"],
     "The variable points to the new object",
     "Reassignment binds the variable name to a new object reference, leaving the old object's reference counter reduced.",
     ["Variables act as named pointers.", "Assignments evaluate right-hand side first.", "Garbage collection manages memory references."]),

    (5, "Expressions and Statements", "05_Expressions_and_Statements.pptx",
     "Decision making using conditional if, elif, and else statements",
     "An expression evaluates to a value. A statement performs an action, such as routing execution blocks based on logical conditions.",
     ["if Statement: Decision-making statement used to execute a block of code only when a specified condition is True.",
      "elif Statement: Used to check multiple conditions in a program. It is placed after an if statement and before an else statement.",
      "else Statement: Acts as a catch-all block that executes if all previous conditions are False.",
      "Key Point: The elif statement helps make decisions when there are more than two possible conditions, making programs more organized and easier to read."],
     ["Dynamic Decision Making: Allows programs to execute different paths based on variables.",
      "Efficient Logic Pathing: Skips remaining elif checks once a True condition is met.",
      "Readable Control Flow: elif prevents deeply nested, hard-to-read if-else structures."],
     ["Logical Masking: Incorrectly ordered conditions can leave code blocks unreachable.",
      "Indentation Dependency: Missing spaces or inconsistent margins break block execution."],
     ["Syntax structure requires colons (:) and block indentation (4 spaces).",
      "elif must follow if, and else must be placed at the very end."],
     "if condition1:\n    # Block 1\nelif condition2:\n    # Block 2\nelse:\n    # Catch-all",
     ["Interpreter evaluates condition to boolean",
      "Executes matching code block if True",
      "Skips remaining elif and else statements",
      "Runs else catch-all block if all checks fail"],
     "num = int(input('Enter an integer: '))\nif num % 2 == 0:\n    print(num, 'is EVEN number.')\nelse:\n    print(num, 'is ODD number.')",
     "Enter an integer: 8\n8 is EVEN number.",
     ["Reads keyboard input and casts to integer",
      "Uses modulo operator % to check parity",
      "Runs if block if divisible by 2, else else block"],
     "marks = int(input('Enter your marks: '))\nif marks >= 90:\n    print('Grade A')\nelif marks >= 75:\n    print('Grade B')\nelif marks >= 60:\n    print('Grade C')\nelse:\n    print('Grade D')",
     "Enter your marks: 82\nGrade B",
     ["Prompts for marks and casts to integer",
      "Checks multiple range conditions sequentially",
      "Exits structure immediately after matching Grade B"],
     ["Forgetting the colon (:) at the end of if/elif/else",
      "Using single equals (=) instead of comparison (==)"],
     ["Always use exactly 4 spaces for block indentation",
      "Order conditions from most specific to most general"],
     ["User permission control routing",
      "Data validation before database writes",
      "Game logic and decision choose pathing"],
     "What is the core purpose of the elif statement?",
     "The elif (else if) statement is used to check multiple conditions sequentially. It runs only if all previous conditions in the chain were False, helping to avoid nested if statements and improving readability.",
     "What happens if multiple conditions in an if-elif chain evaluate to True?",
     "Only the block of the first condition that evaluates to True will execute. Python skips all subsequent elif and else blocks in that chain, regardless of their truth values.",
     "Write a program to test the divisibility of a number by another number (e.g. check if number1 is divisible by number2).",
     "Input two integers: if divisible, print 'Divisible', else print 'Not divisible' along with remainder.",
     "Which keyword acts as a multi-condition branch in Python decision making?",
     ["elseif", "elif", "else if", "switch"],
     "elif",
     "Python uses the compressed keyword 'elif' representing 'else if' to check multiple conditions sequentially.",
     ["Mastered branching using if, elif, and else.",
      "Learned syntax, colons, and indentation rules.",
      "Wrote programs for parity, grades, and divisibility."]),

    (6, "Data Types Overview", "06_Data_Types_Overview.pptx",
     "Built-in basic and collective data types in Python",
     "Data types categorize values, telling the Python interpreter what operations can be performed on them.",
     ["Numeric types represent numbers (int, float, complex).",
      "Sequence types represent ordered values (str, list, tuple).",
      "Set types store unique, unordered elements.",
      "Mapping types store key-value structures (dict)."],
     ["Built-in types optimize memory consumption dynamically.", "Strong type boundaries protect code from unexpected math errors."],
     ["Implicit type conversions can lead to precision loss.", "Immutability forces creating new objects for updates."],
     ["Use type() to identify object data class.", "Determine if collection is mutable or immutable.", "Cast variables using class names (int, str)."],
     "x = 42\ns = 'Text'\nlst = [1, 2]",
     ["PVM instantiates object of target class type", "Assigns value and type ID metadata to object", "Restricts operations based on type class", "Enforces mutable or immutable rules"],
     "num = 42\ns = 'Python'\nprint(type(num), type(s))",
     "<class 'int'> <class 'str'>",
     ["Assigns integer to variable num", "Assigns string to variable s", "Prints the data type classes of both variables"],
     "lst = [1, 2]\nlst[0] = 10\nprint('List:', lst)\ns = 'hello'\n# s[0] = 'H'  # Raises TypeError",
     "List: [10, 2]",
     ["Declares mutable list and updates index 0", "Declares immutable string variable", "Comment explains that string modification raises error"],
     ["Modifying immutable values in place", "Mixing incompatible types in expressions"],
     ["Use lists for mutable sequences and tuples for fixed data", "Check data types with isinstance() instead of type()"],
     ["Data type validations", "Object modeling design", "Database schema conversions"],
     "What is the difference between mutable and immutable data types?",
     "Mutable types (like lists, dicts, sets) can be altered after creation. Immutable types (like ints, floats, strings, tuples) cannot be changed in place.",
     "Why are keys in a dictionary required to be immutable?",
     "Dictionary keys must be hashable. If a key's value could change, its hash value would change, breaking lookup logic.",
     "Write a script that casts a float into an integer and a string.",
     "Demonstrate the type differences between lists, tuples, and sets.",
     "Which of the following data types is immutable in Python?",
     ["List", "Dictionary", "Tuple", "Set"],
     "Tuple",
     "Tuples, strings, integers, and floats are immutable. Lists, dictionaries, and sets are mutable collections.",
     ["Built-in types define data rules.", "Strong type checking protects math.", "Mutability defines copy behaviors."]),

    (7, "Input and Output", "07_Input_and_Output.pptx",
     "Dynamic console input reading and formatted output printing",
     "Input reads user entries from the terminal as string values. Output writes formatted data strings back to the console.",
     ["input() pauses execution and reads user keyboard keystrokes.",
      "input() always returns user input as a string.",
      "print() writes comma-separated objects to console.",
      "print() uses sep and end parameters to format layout."],
     ["Enables interactive, user-driven console scripts.", "sep and end parameters simplify console layout styling."],
     ["Console input reading blocks code execution synchronously.", "String inputs must be cast manually for math operations."],
     ["Pass prompt string inside input().", "Type cast input using int() or float() for math.", "Use formatted string literals (f-strings) in print()."],
     "name = input('Enter name: ')\nprint(f'Hello {name}')",
     ["input() blocks thread and waits for keystrokes", "Reads keystrokes until enter key is pressed", "print() formats and writes string to stdout", "Appends end separator to stream output"],
     "age_str = input('Enter age: ')\nage = int(age_str)\nprint('Next year:', age + 1)",
     "Enter age: 20\nNext year: 21",
     ["Prompts user for input and reads string", "Casts string variable into integer type", "Adds values and prints output to console"],
     "print('Python', 'Course', sep='-', end=' | DONE\\n')",
     "Python-Course | DONE",
     ["Invokes print with two positional string arguments", "Specifies custom separator dash parameter", "Specifies custom end parameter and newline"],
     ["Forgetting to cast input strings to numbers", "Misconfiguring print arguments formatting"],
     ["Always use f-strings for clean console formatting", "Provide clear prompts inside input() instructions"],
     ["Command line utility prompts", "Debug message logging outputs", "User interactive scripts"],
     "Why does input() always return a string value?",
     "To ensure type safety and prevent execution of arbitrary code from raw user console inputs.",
     "How do the sep and end parameters in print() function?",
     "sep specifies the character placed between printed objects (defaults to space). end specifies the character appended to the output string (defaults to newline).",
     "Write a script that reads two numbers from a user and prints their sum.",
     "Show how to print a multi-line formatted message using f-strings.",
     "What is the default value of the end parameter in the print() function?",
     ["space", "empty string", "newline (\\n)", "tab (\\t)"],
     "newline (\\n)",
     "By default, print() appends a newline character (\\n) to the end of the output, moving the cursor to the next line.",
     ["input() returns string values.", "Type cast inputs before math.", "sep and end format print layout."]),

    (8, "Operators and Number Systems", "08_Operators_and_Number_Systems.pptx",
     "Basic operators and number system conversions",
     "Operators compute values on operands. Number systems define representations like Binary, Octal, Decimal, and Hexadecimal.",
     ["Arithmetic operators calculate values (+, -, *, /, //, %, **).",
      "Logical operators evaluate truth tables (and, or, not).",
      "Identity operators check object memory addresses (is, is not).",
      "Built-in functions convert decimal numbers (bin, oct, hex)."],
     ["Identity operators avoid slow value comparisons.", "Built-in conversion methods speed up binary calculations."],
     ["Division always returns a float, requiring floor division.", "Logical operator evaluation short-circuits can skip checks."],
     ["Use double slash (//) for integer floor division.", "Convert integer strings with base parameter in int().", "Identity operator is checks id(), not values."],
     "x = 0b1100\nprint(x)\nhex_val = hex(12)",
     ["Evaluates operands and operator precedence", "Computes binary values on system CPU", "Translates values to decimal display format", "Assigns converted string reference to variable"],
     "print(10 // 3, 10 % 3)\nprint(True and False)",
     "3 1\nFalse",
     ["Performs floor division on operands", "Calculates modulo remainder of division", "Evaluates logical AND truth table operation"],
     "num = 12\nprint('Bin:', bin(num))\nprint('Hex:', hex(num))\nb = 0b1100\nprint('Dec:', b)",
     "Bin: 0b1100\nHex: 0xc\nDec: 12",
     ["Converts integer 12 to binary string", "Converts integer 12 to hex string", "Declares binary literal and prints decimal value"],
     ["Using is operator when value equality == is needed", "Forgetting that division / always returns a float"],
     ["Use is to compare boolean states or None objects", "Verify base prefixes (0b, 0o, 0x) in inputs"],
     ["Cryptographic check scripts", "Binary flag status checks", "Bitwise mask configurations"],
     "What is the difference between the == and is operators?",
     "== compares the values of two objects. is compares whether both variables point to the exact same object address in memory.",
     "Explain how base prefixes indicate number systems in Python.",
     "0b indicates binary (base 2), 0o indicates octal (base 8), and 0x indicates hexadecimal (base 16). No prefix indicates decimal.",
     "Convert a hex string input to a decimal value dynamically.",
     "Demonstrate identity comparison vs value equality with two identical lists.",
     "Which prefix represents a hexadecimal number literal in Python?",
     ["0b", "0o", "0x", "0h"],
     "0x",
     "In Python, binary literals use 0b, octal literals use 0o, and hexadecimal literals use 0x.",
     ["Operators run CPU computations.", "Number systems define bases.", "is operator compares object IDs."]),

    # UNIT 2
    (9, "While Loops", "09_While_Loops.pptx",
     "Conditional execution while boolean check remains true",
     "A while loop repeats a block of code continuously as long as its conditional expression evaluates to True.",
     ["Condition is checked at the start of every loop iteration.",
      "Requires loop counter modification within block to terminate.",
      "Infinite loop occurs if condition never evaluates to False.",
      "Can contain an optional else block that runs upon normal exit."],
     ["Ideal for processing dynamic event streams and user inputs.", "else block helps verify clean, complete loop execution."],
     ["Infinite loops consume system resources, freezing programs.", "Indentation errors in counter increment block breaks loop."],
     ["Declare loop counter outside the loop block.", "Define while keyword with conditional statement.", "Indent all statements to run inside loop."],
     "i = 1\nwhile i <= 3:\n    print(i)\n    i += 1",
     ["Evaluates loop condition to boolean", "Executes indented statements if True", "Updates loop variables inside block", "Returns to condition check step"],
     "i = 1\nwhile i <= 3:\n    print('Loop:', i)\n    i += 1",
     "Loop: 1\nLoop: 2\nLoop: 3",
     ["Initializes counter variable i to 1", "Checks if i <= 3, runs block, prints value", "Increments i by 1 and repeats check"],
     "count = 3\nwhile count > 0:\n    print(count)\n    count -= 1\nelse:\n    print('Finished!')",
     "3\n2\n1\nFinished!",
     ["Initializes countdown counter to 3", "Runs countdown loop, decrementing counter", "Executes else block because loop ended normally"],
     ["Forgetting to increment loop counter, freezing program", "Incorrect indentation placing update outside loop"],
     ["Always include loop break safeguards for live files", "Double check loop variable update logic"],
     ["Reading network streams", "Continuous server polling tasks", "User interface event loops"],
     "What is an infinite loop and how do you break it?",
     "An infinite loop has a condition that never evaluates to False. In the console, you can break it by pressing Ctrl+C.",
     "When does the else block of a while loop execute?",
     "It executes once when the loop condition evaluates to False. If the loop is terminated by a break statement, the else block is skipped.",
     "Write a while loop that reads input until the user types 'exit'.",
     "Show a while loop that processes elements of a list using pop().",
     "What happens to a while loop's else block if a break statement is hit?",
     ["The else block executes once", "The else block is skipped", "The program raises SyntaxError", "The loop repeats indefinitely"],
     "The else block is skipped",
     "A loop else block only executes if the loop terminates normally (condition becomes False). A break terminates it prematurely, skipping else.",
     ["while loops check conditions first.", "Always increment loop counters.", "else block runs on normal exit."]),

    (10, "For Loops", "10_For_Loops.pptx",
     "Sequential iteration and range function execution",
     "A for loop iterates over elements of any sequence (like list, string, tuple) or evaluates values generated by range().",
     ["Iterates sequentially over collections of data values.",
      "Iterates fixed number of times via range(start, stop, step).",
      "Loops stop automatically when sequence ends.",
      "Compatible with loops control blocks like break/continue."],
     ["Eliminates need for manual loop counter management.", "Highly readable sequence and range iteration layouts."],
     ["Cannot easily modify sequence elements during loop.", "Processing large ranges sequentially consumes memory."],
     ["Write for keyword, target variable, and sequence.", "Specify range values with start, stop, and step arguments.", "Indent statements to execute in loop body."],
     "for i in range(3):\n    print(i)",
     ["Interpreter fetches sequence iterator", "Retrieves next value from iterator", "Assigns value to loop variable", "Executes loop body statements"],
     "for i in range(1, 6, 2):\n    print('Val:', i)",
     "Val: 1\nVal: 3\nVal: 5",
     ["Sets up range loop starting at 1, stopping before 6", "Uses step parameter 2 to skip odd values", "Prints values sequentially"],
     "s = 'CSE'\nfor char in s:\n    print('Char:', char)",
     "Char: C\nChar: S\nChar: E",
     ["Initializes string sequence variable", "Loops over each character value in string", "Prints characters one by one"],
     ["Modifying iterated collection inside loop body", "Off-by-one errors with range stop boundary"],
     ["Use range() for numeric iteration counters", "Ensure iterated object is collection sequence"],
     ["List processing scripts", "Automated directory sweeps", "Data mapping operations"],
     "How does range(start, stop, step) generate values?",
     "It generates integers starting from 'start', incrementing by 'step', and stopping right before 'stop'.",
     "Can a for loop iterate over a dictionary?",
     "Yes, by default it iterates over dictionary keys. You can use .values() or .items() to iterate values or key-value pairs.",
     "Write a for loop that calculates sum of numbers in a list.",
     "Show how to loop through a string backward using a for loop.",
     "How many times will a loop with range(2, 8, 2) run?",
     ["3 times", "4 times", "6 times", "8 times"],
     "3 times",
     "The generated values are 2, 4, and 6. 8 is excluded as it is the stop value, so the loop runs 3 times.",
     ["for loops iterate sequences.", "range() stop value is excluded.", "Iterators stop loop automatically."]),

    (11, "Loop Control Statements", "11_Loop_Control_Statements.pptx",
     "Altering loop flows using break, continue, and pass",
     "Loop control statements alter loop execution flow, terminating execution, skipping steps, or placing code placeholders.",
     ["break terminates active loop immediately, jumping to outer code.",
      "continue skips remaining statements in iteration, returning to start.",
      "pass acts as a null statement placeholder for syntactical completeness.",
      "Control statements apply to both while and for loops."],
     ["Prevents unnecessary iterations, optimizing CPU speed.", "pass allows writing clean skeleton templates before coding."],
     ["Overusing break creates code that is difficult to trace.", "continue statements can accidentally bypass update steps."],
     ["Place break inside loop conditional blocks.", "Place continue to skip target elements.", "Use pass inside empty function or loop blocks."],
     "for i in range(5):\n    if i == 3: break",
     ["Interpreter hits control statement", "Branch logic redirects execution path", "Jumps to loop start or exits loop block", "Continues running next sequential code"],
     "for i in range(4):\n    if i == 2: break\n    print(i)",
     "0\n1",
     ["Loops from 0 to 3", "Checks conditional check when variable is 2", "Exits loop body immediately, stopping print"],
     "for i in range(4):\n    if i == 2: continue\n    print(i)",
     "0\n1\n3",
     ["Loops from 0 to 3", "Hits conditional check when variable is 2", "Skips print step for index 2, loops next"],
     ["Forgetting counter updates when skipping in while loop", "Placing statements after break inside loop"],
     ["Use pass for draft skeletons to keep code building", "Keep break conditions clear and simple"],
     ["Search algorithm exit triggers", "Data cleaning filter sweeps", "API skeleton block drafting"],
     "What is the structural purpose of the pass statement?",
     "Python syntax does not allow empty code blocks. pass acts as a placeholder so the code compiles without syntax errors.",
     "How does continue affect a while loop versus a for loop?",
     "In both, it skips the rest of the loop block. In a for loop, it moves to the next item. In a while loop, it checks the condition again.",
     "Write a loop that prints numbers but skips multiples of 3.",
     "Write a loop that breaks if a negative number is encountered.",
     "Which statement immediately stops a loop execution?",
     ["continue", "pass", "break", "exit"],
     "break",
     "break immediately exits the loop block, while continue only skips the remaining code of the current iteration.",
     ["break exits loops immediately.", "continue skips active step.", "pass is empty block placeholder."])
]

# Unpack and add topics 1 to 11 to COURSE_DATA list
for item in SYLLABUS_TOPICS:
    COURSE_DATA.append({
        "id": item[0],
        "title": item[1],
        "filename": item[2],
        "subtitle": item[3],
        "definition": item[4],
        "features": item[5],
        "advantages": item[6],
        "disadvantages": item[7],
        "syntax": item[9],
        "syntax_explanation": item[8],
        "working_steps": item[10],
        "code_basic": item[11],
        "code_basic_out": item[12],
        "code_basic_highlights": item[13],
        "code_complex": item[14],
        "code_complex_out": item[15],
        "code_complex_highlights": item[16],
        "mistakes": item[17],
        "best_practices": item[18],
        "applications": item[19],
        "interview_q1": item[20],
        "interview_a1": item[21],
        "interview_q2": item[22],
        "interview_a2": item[23],
        "practice_q1": item[24],
        "practice_q2": item[25],
        "quiz_q": item[26],
        "quiz_options": item[27],
        "quiz_ans": item[28],
        "quiz_explanation": item[29],
        "summary_points": item[30],
        "references": ["Official Python Docs (docs.python.org)", "Python Programming Core Guide", "Interactive Python Tutorials"]
    })

# We will populate the remaining topics dynamically during construction to keep file size optimized
REMAINING_TOPICS = {
    12: {
        "title": "Introduction to Functions", "fn": "12_Introduction_to_Functions.pptx",
        "sub": "Modular programming using named blocks of code",
        "df": "Functions are named, modular blocks of code designed to perform specific tasks, enabling code reusability and reducing program redundancy.",
        "features": ["Declared using the def keyword with a unique identifier name.", "Accept input parameters inside parentheses.", "Return values back to calling statements via return keyword.", "Local namespaces protect variables inside the function frame."],
        "advantages": [
            "Code Reusability: Write code once and use it multiple times across the program.",
            "Reduces Code Duplication: Eliminates the need to write the same block of code repeatedly.",
            "Improves Readability: Makes programs easier to understand and follow.",
            "Easy Debugging: Errors can be found and fixed in a single location.",
            "Simplifies Maintenance: Updating a function automatically updates it everywhere it is called.",
            "Modular Programming: Breaks large programs into smaller, manageable parts.",
            "Saves Time and Effort: Speeds up program development and testing cycles.",
            "Enhances Collaboration: Different programmers can work on different functions independently."
        ],
        "disadvantages": [
            "Initial Learning Curve: Beginners may find functions difficult to understand at first.",
            "Function Call Overhead: Calling functions repeatedly adds a small stack execution overhead.",
            "Too Many Functions: Excessive use of tiny functions can make code harder to follow and read.",
            "Parameter Management: Passing too many arguments to a function increases complexity.",
            "Debugging Complexity: Tracing execution across multiple functions is harder in large programs."
        ],
        "comparison_table": {
            "headers": ["Basis", "Built-in Functions", "User-defined Functions"],
            "rows": [
                ["Definition", "Functions that are already provided by Python.", "Functions created by the programmer to perform specific tasks."],
                ["Who Creates Them?", "Python developers.", "The programmer or user."],
                ["Availability", "Available by default without defining them.", "Must be defined before they can be used."],
                ["Purpose", "Perform common operations such as input, output, calculations, and type conversion.", "Perform custom tasks according to the program's requirements."],
                ["Syntax", "Called directly using their names.", "Created using the def keyword."],
                ["Modification", "Cannot be modified by the user.", "Can be modified or updated by the programmer."],
                ["Examples", "print(), input(), len(), type(), sum()", "greet(), calculate_total(), find_max()"]
            ]
        },
        "syntax": "def function_name(parameters):\n    return result",
        "working_steps": ["Call triggers function execution", "Allocates frame on system call stack", "Executes statements inside function body", "Returns value and deallocates stack frame"],
        "code_basic": "def greet(name):\n    return 'Hello ' + name\nprint(greet('Learners'))", "code_basic_out": "Hello Learners",
        "code_b_hl": ["Declares simple greeting function with parameter", "Returns combined string expression", "Invokes function and prints output"],
        "code_complex": "def calc_area(r):\n    if r <= 0: return 0\n    return 3.14 * r * r\nprint(calc_area(5))", "code_complex_out": "78.5",
        "code_c_hl": ["Defines area calculation with validation check", "Checks boundary and returns zero if negative", "Calculates float area for valid radius"],
        "mistakes": ["Forgetting to write return keyword when output is needed", "Declaring functions with duplicate identifier names"],
        "best_practices": ["Document function behaviors using triple-quoted docstrings", "Keep functions small and focused on a single task"],
        "apps": ["Modular library engineering", "Reusable calculation toolsets", "Input data validation code"],
        "q1": "How does return differ from print inside functions?", "a1": "print writes data to the console output stream. return exits the function and sends a resulting value back to the calling statement.",
        "q2": "What occurs when a function has no return statement?", "a2": "The function executes its code blocks and returns None automatically when it reaches the end.",
        "pq1": "Write a function that calculates the factorial of a number iteratively.", "pq2": "Create a function that checks if a string is a palindrome.",
        "quiz_q": "Which keyword is used to declare a function in Python?", "opts": ["function", "def", "declare", "define"], "ans": "def",
        "quiz_exp": "Python uses the reserved keyword 'def' to define user-defined functions.",
        "recs": ["Official Python docs on def", "Core Python Programming textbooks", "Modular coding guide modules"]
    },
    13: {
        "title": "Function Arguments", "fn": "13_Function_Arguments.pptx",
        "sub": "Parameter passing, positional mapping, and default argument rules",
        "df": "Arguments represent the actual values passed to parameters during a function call, classified into positional, keyword, and default types.",
        "features": [
            "Positional Arguments: Arguments are mapped to parameters based on their order in the call statement.",
            "Keyword Arguments: Arguments are mapped by parameter name, bypassing call position rules.",
            "Default Parameters: Parameters assigned default values during definition, used if the argument is omitted.",
            "Syntax Ordering: Positional parameters must be placed before default parameters to avoid syntax errors."
        ],
        "advantages": [
            "Flexible Calls: Keyword arguments allow arguments to be specified in any order.",
            "Simplified Invocation: Default arguments reduce redundancy for commonly used parameters."
        ],
        "disadvantages": [
            "Mutable Default Trap: Default lists or dicts are shared across calls, causing mutation side-effects.",
            "Name Match Error: Incorrect keyword argument names raise a TypeError."
        ],
        "syntax": "def func(a, b=10):\n    return a + b",
        "working_steps": [
            "PVM maps passed positional arguments to parameters in order",
            "Matches keyword arguments with corresponding parameter names",
            "Assigns default fallback values to remaining undefined parameters",
            "Initializes local call frame namespace variables"
        ],
        "code_basic": "def greet(name, msg='Hello'):\n    print(f'{msg}, {name}!')\n\ngreet('Anil')\ngreet('Amit', msg='Welcome')",
        "code_basic_out": "Hello, Anil!\nWelcome, Amit!",
        "code_b_hl": [
            "Declares positional parameter name and default parameter msg",
            "Invokes function with single positional argument, using default greeting",
            "Invokes function overwriting default value using keyword argument"
        ],
        "code_complex": "def create_user(username, email, role='User'):\n    return {'username': username, 'email': email, 'role': role}\n\nprint(create_user(email='raj@example.com', username='raj'))",
        "code_complex_out": "{'username': 'raj', 'email': 'raj@example.com', 'role': 'User'}",
        "code_c_hl": [
            "Declares function with two mandatory parameters and one default",
            "Calls function using keyword arguments in arbitrary order",
            "Prints dictionary mapping verifying default role was assigned"
        ],
        "mistakes": [
            "Placing default parameters before non-default parameters in function definitions",
            "Using mutable types like lists or dictionaries as default arguments"
        ],
        "best_practices": [
            "Use None as default for mutable arguments and initialize them inside the function body",
            "Use keyword arguments for functions taking many parameters to improve clarity"
        ],
        "apps": [
            "Configurable library classes and API interfaces",
            "Database client connection setups with fallbacks",
            "GUI component parameter initializations"
        ],
        "q1": "Why must default parameters follow non-default parameters?",
        "a1": "To avoid mapping ambiguity. When a function is called with fewer arguments, Python cannot determine which non-default parameters were omitted if they are placed after defaults.",
        "q2": "What is the mutable default argument trap and how do we resolve it?",
        "a2": "Default values are initialized once when the function is defined. If default is a list, all calls modify the same list object. Resolve by setting default to None and creating list inside.",
        "pq1": "Write a function that calculates total bill, using a tax rate parameter with a default of 5%.",
        "pq2": "Demonstrate the mutable default argument trap using an append function and show the fix.",
        "quiz_q": "Which parameter definition raises a SyntaxError?",
        "opts": ["def f(a=1, b):", "def f(a, b=1):", "def f(a, b=None):", "def f(a, b, c=1):"],
        "ans": "def f(a=1, b):",
        "quiz_exp": "Python requires non-default arguments to be defined before any default arguments.",
        "recs": [
            "Default arguments documentation",
            "Function argument design patterns",
            "Standard parameter guidelines"
        ],
        "comparison_table": {
            "headers": ["Argument Type", "Syntax / Form", "Mapping Mechanism", "Key Advantage", "Rules / Restrictions"],
            "rows": [
                ["Positional", "func(10, 20)", "Mapped by order of appearance", "Fastest execution binding", "Must be passed in exact order"],
                ["Keyword", "func(b=20, a=10)", "Mapped by matching parameter name", "Bypasses strict order rule", "Names must match signature exactly"],
                ["Default", "def func(a, b=10):", "Uses fallback if argument is omitted", "Reduces call-side clutter", "Must follow non-default parameters"]
            ]
        }
    },
    14: {
        "title": "Variable-Length Arguments", "fn": "14_Variable_Length_Arguments.pptx",
        "sub": "Dynamic parameter passing, asterisk packing (*args), and double-asterisk packing (**kwargs)",
        "df": "Variable-length arguments allow Python functions to accept an arbitrary number of positional arguments (packed into a tuple) or keyword arguments (packed into a dictionary).",
        "features": [
            "Positional packing (*args): Accepts arbitrary positional arguments, packing them into a local tuple.",
            "Keyword packing (**kwargs): Accepts arbitrary keyword arguments, packing them into a local dictionary.",
            "Call-side Unpacking (* and **): Unpacks list/tuple into positional arguments, or dictionary into keyword arguments.",
            "Parameter Ordering: Standard parameters must precede *args, which must precede **kwargs in signatures."
        ],
        "advantages": [
            "Highly Flexible: Allows functions to process unpredictable input counts without manual list/dict wrapping.",
            "Dynamic APIs: Enables wrapper functions and decorators to pass arguments through cleanly."
        ],
        "disadvantages": [
            "Reduced Readability: Excessive arguments can make execution flows hard to follow.",
            "Type Checking Overhead: Requires manual validation of items inside packed collections."
        ],
        "syntax": "def func(*args, **kwargs):\n    pass",
        "working_steps": [
            "PVM binds matching standard arguments to parameters",
            "Packs remaining positional arguments into a tuple for *args",
            "Packs remaining keyword arguments into a dictionary for **kwargs",
            "Binds packed variables to respective parameter names"
        ],
        "code_basic": "def show_args(*args, **kwargs):\n    print('args:', args)\n    print('kwargs:', kwargs)\n\nshow_args(1, 2, a=3, b=4)",
        "code_basic_out": "args: (1, 2)\nkwargs: {'a': 3, 'b': 4}",
        "code_b_hl": [
            "Declares positional variable parameter args and keyword variable kwargs",
            "Invokes function passing positional values and keyword pairs",
            "Verifies args is a tuple and kwargs is a dictionary"
        ],
        "code_complex": "def calculate_sum(*nums, **options):\n    total = sum(nums)\n    if options.get('absolute'):\n        total = abs(total)\n    return total\n\nprint(calculate_sum(-10, -20, absolute=True))",
        "code_complex_out": "30",
        "code_c_hl": [
            "Declares function packing numbers into nums tuple and options into options dict",
            "Computes sum of packed numbers using built-in sum()",
            "Checks options dictionary for absolute flag and returns result"
        ],
        "mistakes": [
            "Placing standard parameters after variable-length positional parameters incorrectly",
            "Confusing *args (tuple) and **kwargs (dict) syntax or ordering"
        ],
        "best_practices": [
            "Use descriptive names (like *nums or **configs) when packing specific types",
            "Use *args and **kwargs in decorators to forward arguments to wrapped functions"
        ],
        "apps": [
            "Logging framework wrappers and event handlers",
            "Mathematical aggregator functions",
            "Configuration setup utilities and API endpoints"
        ],
        "q1": "How does Python pack arguments under the hood?",
        "a1": "By dynamically creating a read-only tuple object for positional arguments and a mutable dictionary object for keyword arguments, then mapping these objects to the parameter names in the local namespace.",
        "q2": "What is call-side unpacking and how does it work?",
        "a2": "It uses * or ** at the call site to unpack sequence elements into positional arguments or dictionary items into keyword arguments (e.g. func(*my_list)).",
        "pq1": "Write a function that accepts any count of numbers and returns their mathematical product.",
        "pq2": "Create a decorator function that logs arguments and returns of any wrapped function using *args and **kwargs.",
        "quiz_q": "What data type is created by Python's **kwargs parameter?",
        "opts": ["List", "Dictionary", "Tuple", "Set"],
        "ans": "Dictionary",
        "quiz_exp": "The **kwargs syntax packs variable keyword arguments into a mutable Dictionary.",
        "recs": [
            "Asterisk operators in Python",
            "Unpacking parameters documentation",
            "Dynamic functions parameters"
        ],
        "comparison_table": {
            "headers": ["Parameter Type", "Syntax / Operator", "Packed Data Type", "Binding Mechanism", "Ideal Use Case"],
            "rows": [
                ["Positional Variable-Length", "*args", "Tuple (immutable sequence)", "Packs extra positional values", "Aggregators, math sums, unknown inputs"],
                ["Keyword Variable-Length", "**kwargs", "Dictionary (mutable mapping)", "Packs extra keyword pairs", "Dynamic configurations, settings options"],
                ["Call-side Unpacking", "*collection", "N/A (unpacks sequence)", "Expands collection to positional inputs", "Passing lists/tuples directly to parameters"],
                ["Dict Unpacking", "**dictionary", "N/A (unpacks mapping)", "Expands mapping to keyword inputs", "Passing configuration dicts directly to functions"]
            ]
        }
    },
    15: {
        "title": "Variable Scope and Lambdas", "fn": "15_Variable_Scope_and_Lambdas.pptx",
        "sub": "Variables scopes and anonymous lambda functions",
        "df": "Variable scope defines where an identifier can be accessed. Lambda functions are unnamed, single-line anonymous functions.",
        "features": ["Local variables are declared inside functions and destroyed at exit.", "Global variables are declared outside functions at module level.", "global keyword allows modifying global variables inside local blocks.", "Lambdas contain a single expression evaluated at runtime."],
        "advantages": ["Scope prevents global namespace pollution.", "Lambdas simplify writing quick callback functions."],
        "disadvantages": ["Modifying global variables creates debugging challenges.", "Lambdas cannot contain statements, limiting complexity."],
        "syntax": "lambda arg1, arg2: expression",
        "working_steps": ["Interpreter evaluates lambda expression", "Creates anonymous function object on heap", "Maps local scope variables to frame", "Deallocates frame on local scope exit"],
        "code_basic": "sq = lambda x: x * x\nprint(sq(5))", "code_basic_out": "25",
        "code_b_hl": ["Declares anonymous function calculating square", "Binds lambda expression to variable sq", "Invokes lambda object and prints result"],
        "code_complex": "x = 10\ndef update():\n    global x\n    x = 20\nupdate()\nprint(x)", "code_complex_out": "20",
        "code_c_hl": ["Initializes global variable x to 10", "Declares global x inside local update block", "Modifies global variable, verified by print statement"],
        "mistakes": ["Attempting to write statements like return or print inside lambda", "Modifying global variables without global keyword"],
        "best_practices": ["Limit global keyword usage to keep functions pure", "Keep lambda expressions short and readable"],
        "apps": ["Sort callback algorithms", "State management functions", "Mathematical operations mappings"],
        "q1": "Explain the LEGB scope lookup hierarchy.", "a1": "Python resolves variables sequentially in Local, Enclosing, Global, and Built-in namespaces, returning a NameError if not found.",
        "q2": "Why are lambda functions called anonymous?", "a2": "Because they are created without a name binding, defined inline via the lambda keyword rather than the def keyword.",
        "pq1": "Create a lambda function that checks if a number is even.", "pq2": "Demonstrate name shadowing between local and global variables.",
        "quiz_q": "Which keyword is used to modify a module-level variable inside a function?", "opts": ["nonlocal", "global", "module", "extern"], "ans": "global",
        "quiz_exp": "The global keyword tells the interpreter to bind a local identifier to the module-level global namespace.",
        "recs": ["Variable scope rules", "Lambda functions guidelines", "Namespace resolution documentation"]
    },
    16: {
        "title": "Recursion and Trigonometrics", "fn": "16_Recursion_and_Trigonometrics.pptx",
        "sub": "Function self-calls and math trigonometric computations",
        "df": "Recursion is a programming technique where a function calls itself. Trigonometrics compute mathematical angles using the math module.",
        "features": ["Requires a base case condition to terminate recursive loops.", "Each recursive step moves closer to base case state.", "math module provides trigonometric calculations.", "Trigonometric methods require input angles in radians."],
        "advantages": ["Simplifies complex algorithms like tree traversals.", "Standard math module functions provide high precision."],
        "disadvantages": ["High call stack memory consumption.", "Forgetting base case causes RecursionError (Stack Overflow)."],
        "syntax": "import math\nrad = math.radians(deg)",
        "working_steps": ["PVM invokes recursive call step", "Pushes new frame onto program call stack", "Checks base case termination condition", "Evaluates trigonometric math functions on CPU"],
        "code_basic": "def fact(n):\n    if n <= 1: return 1\n    return n * fact(n - 1)\nprint(fact(4))", "code_basic_out": "24",
        "code_b_hl": ["Declares factorial function utilizing recursion", "Defines base case returning 1 if input is 1", "Triggers recursive multiplication step"],
        "code_complex": "import math\ndeg = 90\nrad = math.radians(deg)\nprint('Sin 90:', math.sin(rad))", "code_complex_out": "Sin 90: 1.0",
        "code_c_hl": ["Imports built-in standard math utility module", "Converts degree value 90 to radians format", "Computes and prints sine calculation value"],
        "mistakes": ["Omitting base case condition in recursive functions", "Passing degree values directly to math.sin or math.cos"],
        "best_practices": ["Check system recursion limit with sys.getrecursionlimit()", "Always convert degree angles to radians before calculation"],
        "apps": ["Mathematical equation solvers", "Data structure traversals", "Scientific calculations systems"],
        "q1": "What is the default recursion limit in Python?", "a1": "It is typically set to 1000 stack frames to prevent infinite execution loop crashes.",
        "q2": "Why must trigonometric inputs be in radians?", "a2": "Python math module functions strictly follow standard mathematical definitions, which expect angle parameters in radians.",
        "pq1": "Write a recursive function that calculates Fibonacci numbers.", "pq2": "Find sine and cosine values of a degree angle input by user.",
        "quiz_q": "What exception is raised when recursion exceeds system limit?", "opts": ["StackOverflowError", "RecursionError", "SystemLimitException", "ValueError"], "ans": "RecursionError",
        "quiz_exp": "Python raises a RecursionError when recursive execution exceeds the maximum depth limit.",
        "recs": ["Recursion limits guides", "Official math module trigonometric functions", "Stack frame trace analysis"]
    },
    17: {
        "title": "Strings and Methods", "fn": "17_Strings_and_Methods.pptx",
        "sub": "String operators, built-in methods, traversal, and reversal",
        "df": "A string is a sequence of characters enclosed within quotation marks, serving as an immutable text data type in computer programming.",
        "features": [
            "String Concatenation: Joining two or more strings together using the + operator.",
            "String Replication: Repeating a string multiple times using the * operator.",
            "String Traversal: Iterating through the elements of a string, one character at a time.",
            "String Searching: Using find() or index() to locate substring positions in slices."
        ],
        "advantages": [
            "Immutable Safety: Strings cannot be modified in-place, making them safe key references.",
            "Rich built-in library: Easy string manipulation using functions like len() and capitalize()."
        ],
        "disadvantages": [
            "Memory Overhead: Re-creating strings during concatenation allocates new memory.",
            "Index Traps: index() raises ValueError if substring is missing, requiring safety checks."
        ],
        "syntax": "result = string.method(sub[, start[, end]])",
        "working_steps": [
            "PVM allocates contiguous memory array for characters",
            "Resolves index boundaries and slice step sizes",
            "Creates temporary string copies during operations",
            "Raises ValueError exception if substring search fails"
        ],
        "code_basic": "first = 'Hello'\nsecond = 'World'\nresult = first + ' ' + second\nprint('Concatenation:', result)\ntext = 'Hi '\nprint('Replication:', text * 3)",
        "code_basic_out": "Concatenation: Hello World\nReplication: Hi Hi Hi ",
        "code_b_hl": [
            "Declares two independent string variables",
            "Uses + operator to concatenate strings with space separator",
            "Uses * operator to repeat text string three times"
        ],
        "code_complex": "string1 = input('Enter a string: ')\nlength = len(string1)\nprint('The python in reverse order is:')\nfor a in range(-1, (-length - 1), -1):\n    print(string1[a])",
        "code_complex_out": "Enter a string: python\nThe python in reverse order is:\nn\no\nh\nt\ny\np",
        "code_c_hl": [
            "Reads console input string and calculates its length",
            "Sets up negative range loop from -1 to -length",
            "Accesses and prints string characters in reverse order, one per line"
        ],
        "mistakes": [
            "Using index() without exception checks, causing ValueError crashes",
            "Expecting capitalize() to only uppercase first letter without lowercasing others",
            "Confusing len() count by omitting spaces which count as valid characters"
        ],
        "best_practices": [
            "Use the in operator instead of find() or index() for simple membership checks",
            "Wrap index() calls in try-except blocks to catch ValueError exceptions safely"
        ],
        "apps": [
            "Text formatting and templating engines",
            "Input validations and pattern matching",
            "Data serialization and parsing operations"
        ],
        "q1": "What is the key difference between find() and index()?",
        "a1": "Both find the lowest index of a substring. However, find() returns -1 if the substring is not found, whereas index() raises a ValueError exception.",
        "q2": "What does string traversal refer to?",
        "a2": "String traversal refers to the process of iterating through the characters of a string one by one, typically using a loop to access each character at its index.",
        "pq1": "Write a script that uses count() to count substring occurrences in a specific index slice.",
        "pq2": "Demonstrate the behavior of capitalize() on strings containing mixed uppercase letters.",
        "quiz_q": "Which operator is used to check the presence of a substring in a string without raising an exception?",
        "opts": ["index()", "find()", "in", "count()"],
        "ans": "in",
        "quiz_exp": "The 'in' operator performs a membership check and returns a boolean (True/False) without raising exceptions.",
        "recs": [
            "String methods reference manual",
            "Sequence traversal and range control docs",
            "Exceptional handling in string searches"
        ],
        "comparison_table": {
            "headers": ["Operation", "Syntax / Form", "Behavior if Not Found / Result"],
            "rows": [
                ["Concatenation", "str1 + str2", "Joins multiple strings together"],
                ["Replication", "str * count", "Repeats the string count times"],
                ["Length", "len(string)", "Returns total count of characters"],
                ["Capitalization", "string.capitalize()", "First letter uppercase, rest lowercase"],
                ["find() Method", "string.find(sub)", "Returns lowest index, or -1 if missing"],
                ["index() Method", "string.index(sub)", "Returns lowest index, or raises ValueError"],
                ["count() Method", "string.count(sub)", "Returns count of occurrences (can be 0)"],
                ["Traversing", "for char in string:", "Iterates one character at a time"]
            ]
        }
    },
    18: {
        "title": "Lists and Operations", "fn": "18_Lists_and_Operations.pptx",
        "sub": "List creation, indexing, slicing, and sequence operators",
        "df": "Lists are mutable, ordered, and heterogeneous sequences in Python that store references to objects and support dynamic size adjustments.",
        "features": [
            "Mutable Sequence: Elements inside lists can be modified in-place without generating a new object.",
            "Heterogeneous Storage: Lists can contain items of different data types, including nested lists.",
            "Indexing & Slicing: Access elements using positive/negative indexes, or extract sublists with [start:stop:step].",
            "Sequence Operators: Supports combination via concatenation (+) and repeating via repetition (*) operators."
        ],
        "advantages": [
            "Dynamic Resizing: Lists dynamically grow and shrink, simplifying data collection management.",
            "Index-based Access: Provides fast O(1) element retrieval when accessing by index position."
        ],
        "disadvantages": [
            "Search Delay: Finding elements by value requires a linear scan, resulting in O(n) search time.",
            "Memory Footprint: Consumes more memory than fixed tuples because lists pre-allocate spare slots."
        ],
        "syntax": "my_list = [item1, item2, item3]",
        "working_steps": [
            "PVM allocates dynamic memory array on the heap",
            "Stores object references in contiguous index slots",
            "Modifies references in-place when updating elements",
            "Increments reference counters for added object elements"
        ],
        "code_basic": "l1 = [10, 20]\nl2 = [30, 40]\ncombined = l1 + l2\nrepeated = l1 * 3\nprint('Concatenation:', combined)\nprint('Replication:', repeated)\nprint('Is 20 in l1?', 20 in l1)",
        "code_basic_out": "Concatenation: [10, 20, 30, 40]\nRepetition: [10, 20, 10, 20, 10, 20]\nIs 20 in l1? True",
        "code_b_hl": [
            "Declares two independent integer list variables",
            "Uses + to concatenate lists, and * to repeat l1 three times",
            "Uses in operator to check element membership in O(n) time"
        ],
        "code_complex": "nums = [10, 20, 30, 40, 50]\nprint('Slicing (step=2):', nums[0:5:2])\nprint('Negative Slicing:', nums[-3:])\nprint('List Traversal:')\nfor idx, val in enumerate(nums):\n    print(f'Index {idx}: {val}')",
        "code_complex_out": "Slicing (step=2): [10, 30, 50]\nNegative Slicing: [30, 40, 50]\nList Traversal:\nIndex 0: 10\nIndex 1: 20\nIndex 2: 30\nIndex 3: 40\nIndex 4: 50",
        "code_c_hl": [
            "Extracts sublist using slicing start, stop, and step arguments",
            "Retrieves last three elements using negative start index slicing",
            "Traverses the list using enumerate to get index-value pairs"
        ],
        "mistakes": [
            "Forgetting that lists store references, leading to unexpected shared mutations",
            "Using out-of-bounds index values during updates, raising IndexError"
        ],
        "best_practices": [
            "Use lists for homogeneous elements and tuples for fixed heterogeneous records",
            "Use copy() or slicing [:] to duplicate lists to avoid modifying original variables"
        ],
        "apps": [
            "Dynamic task queues and buffers",
            "Data record listings in application models",
            "Iterative data processing and accumulation"
        ],
        "q1": "What is the difference between list concatenation and extending a list?",
        "a1": "Concatenation (+) combines lists and returns a brand-new list object, leaving original lists unmodified. Extending modifies the target list in-place.",
        "q2": "How does negative indexing and slicing work in lists?",
        "a2": "Negative indexing accesses elements from right to left (ending at -1). Negative slicing extracts segments relative to the list end.",
        "pq1": "Write a script that swaps the first and last elements of a list dynamically.",
        "pq2": "Create a program that reverses a list using slicing and prints each item.",
        "quiz_q": "Which time complexity represents accessing a list element by its index?",
        "opts": ["O(1)", "O(n)", "O(log n)", "O(n^2)"],
        "ans": "O(1)",
        "quiz_exp": "Accessing an element by index in a Python list takes constant O(1) time because the list is stored in contiguous memory.",
        "recs": [
            "Python lists official guidelines",
            "Dynamic array structures in Python PVM",
            "Slicing and index sequence mapping"
        ],
        "comparison_table": {
            "headers": ["Operation", "Syntax / Form", "Description / Time Complexity"],
            "rows": [
                ["Concatenation", "l1 + l2", "Combines lists into a new list | O(k)"],
                ["Repetition", "l * count", "Repeats list count times | O(k*count)"],
                ["Membership", "item in list", "Scans list for matching value | O(n)"],
                ["Indexing", "list[i] / list[-i]", "Retrieves element at index position | O(1)"],
                ["Slicing", "list[start:stop:step]", "Extracts portion of list as new list | O(k)"],
                ["Length", "len(list)", "Returns number of elements in list | O(1)"],
                ["Clear All", "list.clear()", "Removes all elements from the list | O(1)"],
                ["Traversal", "for item in list:", "Iterates through elements sequentially | O(n)"]
            ]
        }
    },
    19: {
        "title": "List Methods", "fn": "19_List_Methods.pptx",
        "sub": "List modification methods and programs",
        "df": "List methods are built-in functions used to modify list objects, query attributes, or manage queue behaviors in-place.",
        "features": ["append() inserts elements to the end of lists.", "insert() places elements at specific index locations.", "pop() removes and returns elements (defaults to end).", "sort() arranges list elements in ascending order in-place."],
        "advantages": ["In-place modifications reduce memory allocation requirements.", "Built-in sort uses highly optimized Timsort algorithm."],
        "disadvantages": ["In-place methods return None, causing assignment errors.", "insert() requires shifting elements, creating O(n) delay."],
        "syntax": "my_list.append(value)\nmy_list.sort()",
        "working_steps": ["PVM invokes list class method", "Locates element memory references", "Updates references in-place without reallocation", "Returns resulting value or None to program"],
        "code_basic": "lst = [10, 20]\nlst.append(30)\nlst.insert(1, 15)\nprint(lst)", "code_basic_out": "[10, 15, 20, 30]",
        "code_b_hl": ["Declares list with two integer elements", "Appends value 30 to the end of list", "Inserts value 15 at index position 1"],
        "code_complex": "l = [30, 10, 20]\nl.sort()\nprint('Sorted:', l)\nprint('Popped:', l.pop())", "code_complex_out": "Sorted: [10, 20, 30]\nPopped: 30",
        "code_c_hl": ["Declares unordered integer list variable", "Sorts list elements in-place using sort method", "Pops and prints final element from sorted list"],
        "mistakes": ["Writing 'sorted_list = my_list.sort()' (returns None)", "Attempting to pop from an empty list (IndexError)"],
        "best_practices": ["Use pop() for stack behavior (LIFO)", "Use collections.deque for efficient queue operations (FIFO)"],
        "apps": ["Data sorting tools", "Stack trace simulations", "Interactive dynamic inventory lists"],
        "q1": "Why does list.sort() return None instead of the sorted list?", "a1": "To emphasize that the modification occurs in-place, preventing developers from assuming a new copy was allocated.",
        "q2": "Compare the performance of pop() vs pop(0).", "a2": "pop() runs in O(1) constant time. pop(0) runs in O(n) linear time because it forces all remaining elements to shift left in memory.",
        "pq1": "Build a basic stack (LIFO) prototype using list methods.", "pq2": "Insert a number into a sorted list while maintaining sorted order.",
        "quiz_q": "Which method removes and returns the final element of a list?", "opts": ["remove()", "discard()", "pop()", "clear()"], "ans": "pop()",
        "quiz_exp": "The pop() method removes and returns the element at the specified index, defaulting to the final element.",
        "recs": ["List methods reference documentation", "Timsort sorting algorithm analysis", "Dynamic arrays complexity analyses"]
    },
    20: {
        "title": "Tuples and Sets", "fn": "20_Tuples_and_Sets.pptx",
        "sub": "Tuple sequences, immutability, tuple unpacking, and set operations",
        "df": "Tuples are immutable, ordered collections of heterogeneous elements. Sets are unordered, mutable collections of unique, hashable values.",
        "features": [
            "Tuple Immutability: Elements inside a tuple cannot be changed or reassigned after creation, protecting records.",
            "Trailing Comma: Single-element tuples require a trailing comma (e.g., (5,)) to differentiate them from integers.",
            "Tuple Unpacking: Extracts tuple elements directly into multiple variables in a single assignment statement.",
            "Set Operations: Sets support mathematical operations including union (|), intersection (&), and differences."
        ],
        "advantages": [
            "Data Integrity: Immutability prevents accidental modification side-effects during program execution.",
            "High Performance: Tuples are faster to iterate than lists; sets provide O(1) membership lookups."
        ],
        "disadvantages": [
            "No In-place Updates: Modifying a tuple requires allocating and creating a brand-new tuple object.",
            "Access Limits: Sets do not support index-based retrieval or slicing, requiring loops or membership checks."
        ],
        "syntax": "my_tuple = (1, 2, 3)\nmy_set = {1, 2, 3}",
        "working_steps": [
            "PVM allocates fixed-size memory array for the tuple",
            "Initializes hash tables for set collections to filter duplicates",
            "Enforces read-only boundaries on tuple object items",
            "Resolves unpacking assignments sequentially into local namespace"
        ],
        "code_basic": "t1 = (10, 20)\nt2 = (30, 40)\ncombined = t1 + t2\nrepeated = t1 * 2\nsingle_tup = (50,)\nprint('Combined:', combined)\nprint('Single Tuple Type:', type(single_tup))",
        "code_basic_out": "Combined: (10, 20, 30, 40)\nSingle Tuple Type: <class 'tuple'>",
        "code_b_hl": [
            "Declares and combines tuples using concatenation (+) and repetition (*)",
            "Declares single-element tuple using the mandatory trailing comma syntax",
            "Prints combined tuple and verifies single-element class type is tuple"
        ],
        "code_complex": "point = (10, 20, 30)\nx, y, z = point\nprint(f'Unpacked: x={x}, y={y}, z={z}')\ns1 = {1, 2, 3}\ns2 = {3, 4, 5}\nprint('Union:', s1 | s2)\nprint('Intersection:', s1 & s2)",
        "code_complex_out": "Unpacked: x=10, y=20, z=30\nUnion: {1, 2, 3, 4, 5}\nIntersection: {3}",
        "code_c_hl": [
            "Unpacks three-element tuple directly into x, y, and z coordinates",
            "Initializes two sets, filtering duplicate values automatically",
            "Computes set union (|) and set intersection (&) and prints results"
        ],
        "mistakes": [
            "Attempting to reassign values to tuple indexes (raises TypeError)",
            "Defining single-element tuples without a comma (e.g. t = (5) creates an integer)",
            "Using empty curly braces {} to declare empty sets (creates dictionary instead)"
        ],
        "best_practices": [
            "Use tuples for read-only database records, coordinates, and constant configurations",
            "Use set() constructor to declare empty sets and to strip duplicate items from lists"
        ],
        "apps": [
            "Function return values containing multiple parameters",
            "Database connection pools and read-only settings configurations",
            "Unique identifier tracking and set comparison systems"
        ],
        "q1": "Why does a single-element tuple require a trailing comma?",
        "a1": "Without a comma, Python evaluates the parentheses as mathematical operators around the value, resulting in a standard integer or string type.",
        "q2": "What occurs when you assign an empty curly brace {} to a variable?",
        "a2": "Python initializes an empty Dictionary instead of a Set. An empty Set must be initialized using the set() constructor.",
        "pq1": "Write a script that extracts unique elements from a list containing duplicates using sets.",
        "pq2": "Demonstrate tuple unpacking by swapping two variables using tuple assignments.",
        "quiz_q": "What data type is created by the expression: t = (10)?",
        "opts": ["Tuple", "Integer", "List", "SyntaxError"],
        "ans": "Integer",
        "quiz_exp": "Without a trailing comma, the parentheses are parsed as grouping operators. (10) evaluates to the integer 10. To create a tuple, write (10,).",
        "recs": [
            "Tuples and Sets sequence guidelines",
            "Unpacking assignments documentation",
            "Set mathematical operations reference"
        ],
        "comparison_table": {
            "headers": ["Feature", "Tuples", "Sets"],
            "rows": [
                ["Mutability", "Immutable (cannot be modified)", "Mutable (elements can be added/removed)"],
                ["Ordering", "Ordered (maintains insertion order)", "Unordered (no guaranteed order)"],
                ["Duplicates", "Allowed (can store identical items)", "Not Allowed (strictly unique values)"],
                ["Syntax", "Enclosed in parentheses: (1, 2)", "Enclosed in curly braces: {1, 2}"],
                ["Element Access", "Via integer index positions: tup[0]", "Via membership checks or loops only"],
                ["Slicing", "Supported: tup[start:stop]", "Not Supported"],
                ["Lookup Speed", "O(n) linear search for values", "O(1) constant search time using hashing"],
                ["Ideal Use Case", "Fixed records, coordinates, multi-returns", "Removing duplicates, mathematical set logic"]
            ]
        }
    },
    21: {
        "title": "Dictionaries and Methods", "fn": "21_Dictionaries_and_Methods.pptx",
        "sub": "Dictionary mappings, safe lookups, key-value traversals, and methods",
        "df": "Dictionaries are mutable, ordered (since Python 3.7) mappings that store data in key-value pairs, where keys must be unique and hashable (immutable).",
        "features": [
            "Key-Value Mapping: Data is stored as pairs, enabling fast lookup of values using their associated keys.",
            "Key Constraints: Keys must be unique and immutable types (like strings, numbers, or tuples).",
            "Mutable Values: Values are mutable, can duplicate, and can store any Python data object type.",
            "Safe Lookups: Accessing keys safely using get() to avoid KeyError exceptions when keys are missing."
        ],
        "advantages": [
            "Fast Lookups: Key searches run in O(1) constant time under average conditions using hash tables.",
            "Structured Records: Ideal for representing complex structured datasets, like JSON objects."
        ],
        "disadvantages": [
            "Memory Overhead: Consumes more memory than lists because of hash table indexing buffers.",
            "Key Collision Cost: Poor hashing functions can lead to collison delays, though Python handles this well."
        ],
        "syntax": "my_dict = {key: value}",
        "working_steps": [
            "PVM computes hash values for dictionary keys",
            "Maps key hash values to internal storage slots",
            "Retrieves value reference dynamically on key access",
            "Overwrites previous value if duplicate key is assigned"
        ],
        "code_basic": "d = {'name': 'Raj', 'roll': 42}\nprint('Name:', d['name'])\nprint('Age:', d.get('age', 'N/A'))\nprint('Is roll present?', 'roll' in d)",
        "code_basic_out": "Name: Raj\nAge: N/A\nIs roll present? True",
        "code_b_hl": [
            "Initializes dictionary mapping string keys to value objects",
            "Retrieves name via key indexing, and age safely using get()",
            "Checks key presence in O(1) time using in operator"
        ],
        "code_complex": "student = {'name': 'Raj', 'score': 90}\nstudent.update({'score': 95, 'grade': 'A'})\nprint('Key-Value Pairs:')\nfor k, v in student.items():\n    print(f'{k} -> {v}')\nremoved_score = student.pop('score')\nprint('Popped Score:', removed_score)",
        "code_complex_out": "Key-Value Pairs:\nname -> Raj\nscore -> 95\ngrade -> A\nPopped Score: 95",
        "code_c_hl": [
            "Updates score and inserts new grade pair using update()",
            "Traverses key-value pairs concurrently using items() loop",
            "Removes key score and retrieves its value using pop()"
        ],
        "mistakes": [
            "Using direct bracket indexing like dict[key] for missing keys, raising KeyError",
            "Using mutable types (like lists) as dictionary keys, raising TypeError"
        ],
        "best_practices": [
            "Always use get() instead of bracket indexing for optional keys",
            "Use dictionary comprehensions to build or filter mappings dynamically"
        ],
        "apps": [
            "Caching search results for instant retrievals",
            "JSON configuration parsers and API payloads",
            "Database row mapping and object modeling representations"
        ],
        "q1": "Why must dictionary keys be immutable in Python?",
        "a1": "Keys must be hashable. If a key's value could change, its hash value would also change, making it impossible to locate the stored value again.",
        "q2": "What are the advantages of using the get() method over bracket indexing?",
        "a2": "Bracket indexing raises a KeyError if the key is missing. The get() method returns a fallback default (or None) without raising exceptions.",
        "pq1": "Write a script that counts character frequencies in a string using a dictionary.",
        "pq2": "Create a program that merges two dictionaries, updating overlapping keys.",
        "quiz_q": "Which method returns a default value instead of raising a KeyError if a key is not found?",
        "opts": ["keys()", "update()", "get()", "pop()"],
        "ans": "get()",
        "quiz_exp": "The get() method returns the value for the key if present, or a fallback default value (defaulting to None) if missing.",
        "recs": [
            "Official dictionary mapping manuals",
            "Hash table implementations in Python PVM",
            "JSON payloads and dictionary configurations"
        ],
        "comparison_table": {
            "headers": ["Method / Operation", "Syntax / Example", "Description / Time Complexity"],
            "rows": [
                ["Indexing Access", "dict[key]", "Retrieves key value; raises KeyError | O(1)"],
                ["Safe Access", "dict.get(key, default)", "Retrieves key value; returns default if missing | O(1)"],
                ["Update / Merge", "dict.update(other)", "Updates/adds key-value pairs in-place | O(k)"],
                ["Key Removal", "dict.pop(key)", "Removes key and returns its value | O(1)"],
                ["Get Keys", "dict.keys()", "Returns a dynamic view of all keys | O(1)"],
                ["Get Values", "dict.values()", "Returns a dynamic view of all values | O(1)"],
                ["Get Items", "dict.items()", "Returns a dynamic view of all key-value tuples | O(1)"],
                ["Membership", "key in dict", "Checks if key is present in dictionary | O(1)"]
            ]
        }
    },
    22: {
        "title": "Comprehensions", "fn": "22_Comprehensions.pptx",
        "sub": "Concise collections creation syntax",
        "df": "Comprehensions provide a concise syntax for constructing new sequences (lists, sets, dictionaries) from existing iterables.",
        "features": ["Construct collections in a single line of code.", "Support inline conditional checks (if filters).", "List comprehensions output new list objects.", "Set and Dictionary comprehensions use curly braces."],
        "advantages": ["Significantly reduces boilerplate code loops.", "Highly optimized bytecode compilation speed."],
        "disadvantages": ["Complex nested comprehensions reduce readability.", "High memory consumption if list is extremely large."],
        "syntax": "[expr for item in iterable if cond]",
        "working_steps": ["PVM initializes destination collection", "Iterates over source sequence elements", "Applies conditional validation checks", "Appends evaluated expressions to destination"],
        "code_basic": "nums = [1, 2, 3]\nsq = [x*x for x in nums]\nprint(sq)", "code_basic_out": "[1, 4, 9]",
        "code_b_hl": ["Initializes base numeric list collection", "Constructs square list using list comprehension", "Prints generated list values"],
        "code_complex": "nums = [1, 2, 3, 4]\neven_sq = {x: x*x for x in nums if x % 2 == 0}\nprint(even_sq)", "code_complex_out": "{2: 4, 4: 16}",
        "code_c_hl": ["Initializes integer collection list", "Executes dictionary comprehension mapping even numbers", "Prints generated key-value pairings"],
        "mistakes": ["Writing nested loops inside one comprehension, reducing readability", "Using comprehensions when simple loops are clearer"],
        "best_practices": ["Keep comprehensions to a single line only", "Use generator expressions for very large datasets"],
        "apps": ["Data transformation steps", "Filtering data lists", "Dynamic mapping dictionary generation"],
        "q1": "How does a generator expression differ from list comprehension?", "a1": "List comprehension evaluates all values immediately in memory. Generator expressions use lazy evaluation, generating items on demand.",
        "q2": "Can you use if-else conditions inside comprehensions?", "a2": "Yes, by placing the if-else expression before the for loop construct (e.g. [x if x > 0 else 0 for x in nums]).",
        "pq1": "Write a list comprehension that extracts uppercase characters from a string.", "pq2": "Create a dictionary comprehension mapping numbers 1-5 to their cubes.",
        "quiz_q": "What is the output of: [x for x in range(5) if x % 2 != 0]?", "opts": ["[0, 2, 4]", "[1, 3]", "[1, 2, 3]", "[0, 1, 3]"], "ans": "[1, 3]",
        "quiz_exp": "The comprehension loops from 0 to 4, filtering out even numbers and keeping only odd values.",
        "recs": ["Comprehensions guidelines", "Generator expressions documentation", "Data piping tutorials"]
    },
    23: {
        "title": "Introduction to OOP", "fn": "23_Introduction_to_OOP.pptx",
        "sub": "Object Oriented programming concepts and paradigms",
        "df": "Object-Oriented Programming (OOP) is a programming paradigm that organizes software design around data objects rather than functions.",
        "features": ["Classes act as blueprints defining attributes and behaviors.", "Objects are instances created from class definitions.", "Supports encapsulation to hide internal data states.", "Enables polymorphism to reuse method interfaces."],
        "advantages": ["Improves codebase modularity and design structures.", "Facilitates code maintenance in large applications."],
        "disadvantages": ["Requires a shift in programming mindset from procedural.", "Small execution overhead due to object metadata."],
        "syntax": "class ClassName:\n    # class blueprint",
        "working_steps": ["PVM loads class definition block", "Registers class in system namespace", "Instantiates objects on program heap", "Binds object methods to namespaces"],
        "code_basic": "class Learner:\n    pass\nobj = Learner()\nprint(type(obj))", "code_basic_out": "<class '__main__.Learner'>",
        "code_b_hl": ["Declares class blueprint using pass keyword", "Instantiates object instance from class blueprint", "Prints class type identifier of instance"],
        "code_complex": "class Room:\n    width = 10\nr = Room()\nprint('Width is:', r.width)", "code_complex_out": "Width is: 10",
        "code_c_hl": ["Defines Room class with class variable", "Creates instance variable room object r", "Accesses width attribute and prints value"],
        "mistakes": ["Confusing classes with objects during variable calls", "Declaring class variables when instance variables are needed"],
        "best_practices": ["Use PascalCase naming convention for class identifiers", "Design classes to model real-world concepts"],
        "apps": ["System domain designs", "User management tools", "Modular GUI software libraries"],
        "q1": "Explain how OOP differs from procedural programming.", "a1": "Procedural programming organizes code around sequential steps. OOP bundles data and related actions into modular objects.",
        "q2": "What are class attributes?", "a2": "Variables defined directly inside the class block, shared by all instances of that class.",
        "pq1": "Define a simple Book class with title and author class variables.", "pq2": "Instantiate three distinct objects from a custom Laptop class blueprint.",
        "quiz_q": "Which term describes a class blueprint instance?", "opts": ["Method", "Variable", "Object", "Function"], "ans": "Object",
        "quiz_exp": "An Object is a concrete instance of a class blueprint created in memory.",
        "recs": ["OOP paradigms guides", "Python class definitions", "Domain modeling guides"]
    },
    24: {
        "title": "OOP Classes and Objects", "fn": "24_OOP_Classes_and_Objects.pptx",
        "sub": "Defining classes and instantiating objects",
        "df": "Classes define target object models, specifying properties (attributes) and actions (methods) that instances can perform.",
        "features": ["class keyword begins class definition blocks.", "Instance attributes store values unique to instances.", "Methods are functions defined inside class blocks.", "Methods must accept 'self' parameter as first argument."],
        "advantages": ["Enables data encapsulation and scoping structures.", "Supports modeling complex software states cleanly."],
        "disadvantages": ["Accessing object attributes creates namespace lookup overhead.", "Can complicate simple, script-based automation tasks."],
        "syntax": "class Dog:\n    def bark(self):\n        print('Woof')",
        "working_steps": ["PVM compiles class definition block", "Allocates memory address for new instance", "Invokes class methods via object namespace", "Passes object instance reference to self"],
        "code_basic": "class Dog:\n    def bark(self):\n        print('Woof!')\nd = Dog()\nd.bark()", "code_basic_out": "Woof!",
        "code_b_hl": ["Declares Dog class with bark method", "Creates object instance of Dog class", "Invokes bark method using dot notation"],
        "code_complex": "class Student:\n    name = 'Anil'\n    def show(self):\n        print('Student:', self.name)\ns = Student()\ns.show()", "code_complex_out": "Student: Anil",
        "code_c_hl": ["Declares Student class with name attribute", "Defines show method accessing attribute via self", "Prints student name from instantiated object"],
        "mistakes": ["Forgetting to write self parameter inside class methods", "Calling class methods without parentheses"],
        "best_practices": ["Always use self to reference instance attributes", "Keep class properties and methods logically organized"],
        "apps": ["User registration forms", "Inventory control programs", "Game character modeling designs"],
        "q1": "Why is the self parameter necessary in class methods?", "a1": "self represents the specific object instance calling the method, allowing access to instance variables.",
        "q2": "What occurs when you modify a class attribute?", "a2": "The modification updates the attribute value for all instances that share that class attribute.",
        "pq1": "Create a Calculator class with add and subtract methods.", "pq2": "Define a Employee class with custom instance attributes.",
        "quiz_q": "What parameter binds class methods to instance objects?", "opts": ["this", "self", "class", "object"], "ans": "self",
        "quiz_exp": "Python uses the 'self' parameter to reference the specific instance calling the method.",
        "recs": ["Classes and Methods documentation", "Object-oriented program designs", "Self parameter explanations"]
    },
    25: {
        "title": "OOP Constructors and Self", "fn": "25_OOP_Constructors_and_Self.pptx",
        "sub": "Object state initialization with constructors",
        "df": "Constructors are special methods used to initialize object states during instantiation, utilizing the self parameter.",
        "features": ["__init__ method is Python's built-in object constructor.", "Invoked automatically when a new object is created.", "Initializes instance attributes with custom arguments.", "self binds constructor operations to the new instance address."],
        "advantages": ["Ensures objects are initialized with valid starting state data.", "Simplifies passing parameters during object creation."],
        "disadvantages": ["Forgetting init double underscores raises attribute errors.", "Constructors cannot return values other than None."],
        "syntax": "class Student:\n    def __init__(self, name):\n        self.name = name",
        "working_steps": ["PVM reserves memory for new object", "Invokes __init__ constructor method", "Passes arguments to instance attributes", "Returns initialized instance reference"],
        "code_basic": "class Student:\n    def __init__(self, name):\n        self.name = name\ns = Student('Raj')\nprint(s.name)", "code_basic_out": "Raj",
        "code_b_hl": ["Defines constructor with initialization argument", "Creates Student object passing value 'Raj'", "Verifies name attribute initialization"],
        "code_complex": "class Point:\n    def __init__(self, x, y):\n        self.x = x\n        self.y = y\np = Point(4, 5)\nprint('Coords:', p.x, p.y)", "code_complex_out": "Coords: 4 5",
        "code_c_hl": ["Defines Point class with two coordinates constructor", "Instantiates point passing values 4 and 5", "Prints instance coordinate values"],
        "mistakes": ["Spelling __init__ with single underscores instead of double", "Attempting to return custom values from constructor"],
        "best_practices": ["Keep constructor calculations minimal and focused on state", "Document expected argument data types"],
        "apps": ["Database connector components", "Network session setups", "Game character state setups"],
        "q1": "Can a class have multiple constructors in Python?", "a1": "No. Python does not support method overloading. The last defined __init__ method will overwrite any previous definitions.",
        "q2": "What happens if a class does not define an __init__ method?", "a2": "Python calls an empty default constructor, creating the object instance with no custom attributes.",
        "pq1": "Write a Book class with a constructor that initializes title, author, and price.", "pq2": "Show how to define default argument values inside a constructor.",
        "quiz_q": "Which method serves as the class constructor in Python?", "opts": ["__init__()", "constructor()", "new()", "create()"], "ans": "__init__()",
        "quiz_exp": "The double underscore __init__ method acts as the initializer/constructor for Python class objects.",
        "recs": ["Python constructors guides", "Double underscore methods", "Object state management docs"]
    },
    26: {
        "title": "OOP Inheritance and Abstraction", "fn": "26_OOP_Inheritance_and_Abstraction.pptx",
        "sub": "Inheritance types overriding data hiding and abstraction",
        "df": "Inheritance enables a child class to inherit properties from a parent class. Abstraction and data hiding obscure implementation details.",
        "features": ["Child classes inherit attributes and methods from parent classes.", "super() function invokes parent class methods.", "Data hiding uses double underscores (__) to make variables private.", "Abstract classes act as templates for child classes."],
        "advantages": ["Promotes code reuse, minimizing code duplication.", "Private attributes prevent accidental external modifications."],
        "disadvantages": ["Tight coupling between parent and child classes.", "Private variables can complicate debugging access."],
        "syntax": "class Child(Parent):\n    def __init__(self):\n        super().__init__()",
        "working_steps": ["PVM links child class to parent namespace", "Resolves method calls using Method Resolution Order", "Applies name mangling to private variables", "Enforces abstract template restrictions"],
        "code_basic": "class P:\n    def show(self): print('Parent')\nclass C(P):\n    def show(self):\n        super().show()\n        print('Child')\nC().show()", "code_basic_out": "Parent\nChild",
        "code_b_hl": ["Defines Parent class with show method", "Defines Child inheriting Parent and overriding show", "Calls parent method using super() and prints Child"],
        "code_complex": "class Hidden:\n    def __init__(self): self.__val = 42\nobj = Hidden()\n# print(obj.__val)  # Raises AttributeError", "code_complex_out": "AttributeError",
        "code_c_hl": ["Defines private variable using double underscores", "Instantiates Hidden class object", "Comments out statement showing direct access raises error"],
        "mistakes": ["Forgetting to invoke parent constructor in child class", "Confusing method overriding with method overloading"],
        "best_practices": ["Use inheritance to represent 'is-a' relationships", "Protect internal variables using private namespaces"],
        "apps": ["UI component design libraries", "Payment gateway adapters", "Standard API clients layouts"],
        "q1": "Explain name mangling in Python.", "a1": "Private variables like __val are internally renamed to _ClassName__val to prevent namespace conflicts in subclass inheritance.",
        "q2": "What is the role of super()?", "a2": "It returns a proxy object that delegates method calls to a parent or sibling class, ensuring correct Method Resolution Order (MRO).",
        "pq1": "Create a Vehicle parent class and a Car child class.", "pq2": "Demonstrate data hiding by creating a BankAccount class with private balance attribute.",
        "quiz_q": "Which function is used to invoke a parent class method?", "opts": ["parent()", "super()", "base()", "ancestor()"], "ans": "super()",
        "quiz_exp": "The super() function resolves class inheritance hierarchies, allowing access to parent class methods.",
        "recs": ["Inheritance structures guide", "Polymorphism and Data Hiding docs", "Method resolution order guides"]
    },
    27: {
        "title": "File Paths and Handling", "fn": "27_File_Paths_and_Handling.pptx",
        "sub": "Filesystem path rules and file handling operations",
        "df": "File handling enables applications to read or write persistent data files on storage drives using absolute or relative paths.",
        "features": ["Absolute paths specify complete directory paths from drive root.", "Relative paths locate files relative to current working directory.", "open() modes specify read (r), write (w), and append (a) actions.", "with context manager closes files automatically on exit."],
        "advantages": ["Context managers prevent file memory leaks.", "File updates persist data after program terminates."],
        "disadvantages": ["Incorrect file paths raise FileNotFoundError.", "Write mode (w) overwrites existing file content."],
        "syntax": "with open(path, mode) as f:\n    content = f.read()",
        "working_steps": ["PVM requests file handle from OS kernel", "Validates file path and access permissions", "Performs read or write streams on disk", "Closes stream handles to release resources"],
        "code_basic": "with open('t.txt', 'w') as f:\n    f.write('Python')\nwith open('t.txt', 'r') as f:\n    print(f.read())", "code_basic_out": "Python",
        "code_b_hl": ["Creates text file using write mode", "Writes string content to text file", "Opens file in read mode and prints content"],
        "code_complex": "with open('t.txt', 'w') as f:\n    f.write('Line 1\\nLine 2\\n')\nwith open('t.txt', 'r') as f:\n    for line in f:\n        print(line.strip())", "code_complex_out": "Line 1\nLine 2",
        "code_c_hl": ["Writes multiple lines with newline characters", "Opens file and iterates over file object line-by-line", "Removes trailing newline spacing and prints"],
        "mistakes": ["Opening files without using with, causing file leaks", "Confusing relative path locations in nested directories"],
        "best_practices": ["Always use with context managers for file operations", "Use raw strings (r'path') for Windows paths containing backslashes"],
        "apps": ["Application log files", "Local setting configurations", "Data record export scripts"],
        "q1": "How does relative path differ from absolute path?", "a1": "Absolute paths specify the full path starting from the root directory. Relative paths resolve starting from the program's working directory.",
        "q2": "What occurs if you open a missing file in append mode?", "a2": "Python creates a new empty file at the target path instead of raising a FileNotFoundError.",
        "pq1": "Write a program that copies contents of one text file to another.", "pq2": "Count the number of lines inside a text file using python.",
        "quiz_q": "Which mode is used to open a file for adding data without overwriting?", "opts": ["'r'", "'w'", "'a'", "'x'"], "ans": "'a'",
        "quiz_exp": "The append mode ('a') opens a file for writing, placing new data at the end of the file without altering existing content.",
        "recs": ["File operations guide", "Context manager structures", "Path configurations tutorial"]
    },
    28: {
        "title": "Errors and Exceptions", "fn": "28_Errors_and_Exceptions.pptx",
        "sub": "Syntax compile and runtime error analysis",
        "df": "Errors are program defects categorized into syntax errors (checked during compilation) and exceptions (runtime failures).",
        "features": ["Syntax errors occur during code parsing before execution.", "Exceptions represent runtime failures during program execution.", "Traceback reports error types and execution line locations.", "Built-in exceptions indicate specific failure types (KeyError, TypeError)."],
        "advantages": ["Traceback details speed up code debugging.", "Exception structures help isolate runtime failures safely."],
        "disadvantages": ["Unhandled exceptions crash active applications.", "Hiding tracebacks can obscure underlying program bugs."],
        "syntax": "# Syntax error example:\n# if True print('hi')",
        "working_steps": ["Interpreter parses code tokens", "Validates syntax structures", "Raises SyntaxError if parsing fails", "Raises Exception objects during runtime failures"],
        "code_basic": "# Syntax Error Example\n# if True print('hi')\n# Output: SyntaxError: invalid syntax", "code_basic_out": "SyntaxError: invalid syntax",
        "code_b_hl": ["Shows comment block of syntax error code", "Highlights missing colon after conditional statement", "Displays resulting parser error message"],
        "code_complex": "# Runtime Exception Example\nx = 10 / 0  # ZeroDivisionError", "code_complex_out": "ZeroDivisionError: division by zero",
        "code_c_hl": ["Declares division calculation", "Attempts to divide integer value by zero", "Raises ZeroDivisionError runtime exception"],
        "mistakes": ["Ignoring exception tracebacks during troubleshooting", "Confusing syntax compiler errors with runtime exceptions"],
        "best_practices": ["Read tracebacks from bottom to top to find line numbers", "Test edge-case inputs to identify potential runtime exceptions"],
        "apps": ["Software debugging processes", "Log tracking tools", "Automated error diagnostic systems"],
        "q1": "Explain the difference between SyntaxError and Exceptions.", "a1": "SyntaxError occurs when code violates parsing rules, preventing compilation. Exceptions occur during execution of syntactically correct code.",
        "q2": "What information does a traceback provide?", "a2": "It shows the execution path, including function calls, filenames, line numbers, and the exception type and message.",
        "pq1": "Write a script that triggers and prints a ValueError traceback.", "pq2": "Fix a syntax error code snippet by adding correct indentation and colons.",
        "quiz_q": "Which error type is checked BEFORE code execution begins?", "opts": ["TypeError", "KeyError", "SyntaxError", "IndexError"], "ans": "SyntaxError",
        "quiz_exp": "Syntax errors are caught by the parser during compilation before the interpreter executes the script.",
        "recs": ["Errors and Exceptions official guide", "Traceback analysis tutorials", "Debugging workflows guide"]
    },
    29: {
        "title": "Exception Handling Operations", "fn": "29_Exception_Handling_Operations.pptx",
        "sub": "Graceful exception handling try except and raise",
        "df": "Exception handling allows programs to catch and process runtime exceptions gracefully using try, except, else, and finally blocks.",
        "features": ["try block contains code that might raise exceptions.", "except block processes specified exceptions gracefully.", "else block executes if no exceptions were raised.", "finally block always executes, ensuring resource cleanup."],
        "advantages": ["Prevents unexpected crashes, keeping applications running.", "finally blocks ensure cleanup (like closing files or database connections)."],
        "disadvantages": ["Broad except blocks can hide unexpected logic bugs.", "Handling exceptions adds minimal execution time."],
        "syntax": "try:\n    # code\nexcept Exception as e:\n    # handle",
        "working_steps": ["PVM enters try block statement", "Monitors execution for runtime exceptions", "Jumps to matching except block if exception occurs", "Executes finally block statements at exit"],
        "code_basic": "try:\n    x = 10 / 0\nexcept ZeroDivisionError:\n    print('Zero division caught')", "code_basic_out": "Zero division caught",
        "code_b_hl": ["Wraps division statement in try block", "Catches division by zero exception using except", "Prints custom error message instead of crashing"],
        "code_complex": "try:\n    raise ValueError('Manual Error')\nexcept ValueError as e:\n    print('Caught:', e)\nfinally:\n    print('Done')", "code_complex_out": "Caught: Manual Error\nDone",
        "code_c_hl": ["Raises ValueError exception manually", "Catches exception and prints message", "Executes finally block print statement at exit"],
        "mistakes": ["Using empty except: statements (catches all exceptions, including exit requests)", "Forgetting to clean up open file resources inside finally blocks"],
        "best_practices": ["Always catch specific exceptions (like FileNotFoundError)", "Use finally blocks to guarantee resource release"],
        "apps": ["Database connector routines", "User input verification scripts", "Network client connection error checks"],
        "q1": "When does the else block execute in exception handling?", "a1": "Only when the code inside the try block runs successfully without raising any exceptions.",
        "q2": "Why should you avoid using bare except: blocks?", "a2": "Because they catch all exceptions, including system exits (SystemExit, KeyboardInterrupt), making debugging difficult.",
        "pq1": "Write a script that handles division of user input, catching value and division errors.", "pq2": "Create a file reading script with robust try-except-finally blocks.",
        "quiz_q": "Which block in exception handling is GUARANTEED to execute?", "opts": ["try", "except", "else", "finally"], "ans": "finally",
        "quiz_exp": "The finally block always runs when exiting the try-except structure, regardless of whether exceptions occurred.",
        "recs": ["Exception handling guidelines", "Built-in exceptions definitions", "Resource cleanup guidelines"]
    },
    30: {
        "title": "Modules, Packages, and Regex", "fn": "30_Modules_Packages_and_Regex.pptx",
        "sub": "Standard library modules, package structures, and regular expressions",
        "df": "Modules are separately saved files containing reusable Python code. Packages organize modules. Regular expressions parse text using standard pattern matching.",
        "features": [
            "Standard Modules: Math module provides mathematical functions; Statistics module provides mean, median, mode; Random module provides random values.",
            "Package Structure: Directories containing modules and a mandatory __init__.py file to mark the package namespace.",
            "Module Import: Loaded using import or from...import statements; custom aliases can be created with 'as'.",
            "Regular Expressions: re module provides powerful search, match, and replace functions for string patterns."
        ],
        "advantages": [
            "Code Reuse: Modules allow identical code to be shared across multiple independent scripts.",
            "Namespace Protection: Modules keep variables isolated, avoiding name collision errors."
        ],
        "disadvantages": [
            "Module Overload: Excess imports slow startup speed and increase memory use.",
            "Regex Complexity: Regex syntax patterns can be difficult to read and debug."
        ],
        "syntax": "import math\nfrom statistics import mean\nimport re",
        "working_steps": [
            "PVM searches sys.path list locations for module file",
            "Compiles imported module file to bytecode in __pycache__",
            "Executes module statements, building module namespace object",
            "Maps imported elements in local program symbol table namespace"
        ],
        "code_basic": "import math\nimport statistics\nimport random\n\nprint('sqrt:', math.sqrt(25))\nprint('mean:', statistics.mean([10, 20, 30]))\nprint('rand:', random.randint(1, 10))",
        "code_basic_out": "sqrt: 5.0\nmean: 20.0\nrand: 7",
        "code_b_hl": [
            "Imports math, statistics, and random standard modules",
            "Invokes math.sqrt(), statistics.mean(), and random.randint()",
            "Prints results calculated using standard library helpers"
        ],
        "code_complex": "import re\ntext = 'User email is raj@example.com'\npattern = r'\\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Z|a-z]{2,}\\b'\nmatch = re.search(pattern, text)\nif match:\n    print('Found email:', match.group())",
        "code_complex_out": "Found email: raj@example.com",
        "code_c_hl": [
            "Imports regular expressions re module library",
            "Defines email search regex pattern containing character classes",
            "Uses re.search() to find pattern and prints group match"
        ],
        "mistakes": [
            "Circular import errors where module A imports B and B imports A",
            "Creating custom files with names identical to standard modules (e.g. math.py)"
        ],
        "best_practices": [
            "Only import the specific functions required from modules using from...import to save namespace clutter",
            "Use raw string prefixes (r'...') for regular expression patterns to avoid backslash escaping conflicts"
        ],
        "apps": [
            "Data analysis using math, statistics, and random numbers",
            "Web scraping and input text format validation filters",
            "Structured package development for custom APIs"
        ],
        "q1": "What is the difference between import module and from module import func?",
        "a1": "import module loads the module namespace, requiring dot prefix access (e.g. module.func()). from...import binds func directly to local namespace, bypassing prefixes.",
        "q2": "What is the purpose of __init__.py in Python packages?",
        "a2": "It marks the directory as a Python package, allowing nested modules to be imported using dot notation, and initializes package-level variables.",
        "pq1": "Write a script that calculates mean, median, and mode of a list using the statistics module.",
        "pq2": "Create a script that generates two random numbers between 450 and 950 and calculates their average using the random module.",
        "quiz_q": "Which regex character matches the start of a string sequence?",
        "opts": ["$", "^", "*", "+"],
        "ans": "^",
        "quiz_exp": "The caret (^) symbol acts as an anchor pointing to the start of a string sequence in regular expressions.",
        "recs": [
            "Modules and Packages documentation",
            "Regular expressions official tutorial",
            "Package structure guidelines"
        ],
        "comparison_table": {
            "headers": ["Concept", "Structure / Format", "Import Syntax", "Key Benefit / Purpose"],
            "rows": [
                ["Modules", "Single Python code file (.py)", "import name", "Reusable units of code and variables"],
                ["Packages", "Folder containing modules and __init__.py", "from pkg import mod", "Organizes modules into hierarchy namespaces"],
                ["Standard Modules", "Built-in libraries (math, stats, random)", "import math, statistics, random", "Common math, statistics, and random number utilities"],
                ["Regular Expressions", "Search patterns for text parsing", "import re; re.search()", "Powerful pattern search, match, and replace"]
            ]
        }
    }
}

# Merge remaining topics into COURSE_DATA
for key, data in REMAINING_TOPICS.items():
    COURSE_DATA.append({
        "id": key,
        "title": data["title"],
        "filename": data["fn"],
        "subtitle": data["sub"],
        "definition": data["df"],
        "features": data["features"],
        "advantages": data["advantages"],
        "disadvantages": data["disadvantages"],
        "syntax": data["syntax"],
        "code_basic": data["code_basic"],
        "code_basic_out": data["code_basic_out"],
        "code_complex": data["code_complex"],
        "code_complex_out": data["code_complex_out"],
        "working_steps": data["working_steps"],
        "mistakes": data["mistakes"],
        "best_practices": data["best_practices"],
        "applications": data["apps"],
        "interview_q1": data["q1"],
        "interview_a1": data["a1"],
        "interview_q2": data["q2"],
        "interview_a2": data["a2"],
        "practice_q1": data["pq1"],
        "practice_q2": data["pq2"],
        "quiz_q": data["quiz_q"],
        "quiz_options": data["opts"],
        "quiz_ans": data["ans"],
        "quiz_explanation": data["quiz_exp"],
        "summary_points": [
            "Analyzed standard definitions and behaviors.",
            "Wrote simple and complex scripts with traces.",
            "Learned core best practices and interview concepts."
        ],
        "references": data["recs"],
        "comparison_table": data.get("comparison_table")
    })

# Update Topic 3 in COURSE_DATA dynamically with professional keywords content
for item in COURSE_DATA:
    if item["id"] == 3:
        item["title"] = "Comments, Identifiers, and Keywords"
        item["filename"] = "03_Comments_and_Identifiers.pptx"
        item["subtitle"] = "Code comments, naming conventions, and reserved keywords"
        item["definition"] = "Python programs utilize comments for documentation, identifiers for naming program entities, and keywords to define syntax and flow rules."
        item["features"] = [
            "Comments Syntax: Inline comments use the hash symbol (#) and multi-line comments use triple quotes.",
            "Identifier Rules: Identifiers name variables/functions; they must begin with letters or underscores, not numbers.",
            "Reserved Keywords: Keywords are reserved words with fixed, predefined meanings that cannot be reassigned.",
            "Case Sensitivity: Python identifiers are case-sensitive; tax, Tax, and TAX are treated as separate identifiers."
        ]
        item["advantages"] = [
            "Clear Structure: Keywords help define the control flow and structure of code clearly.",
            "Self-Documenting: Clean comments and descriptive identifier names improve code readability."
        ]
        item["disadvantages"] = [
            "Restricted Naming: Keywords cannot be used as identifiers, which limits naming choices slightly.",
            "Stale Documentation: Outdated comments confuse developers if code changes without updates."
        ]
        item["syntax"] = "# Comment\nx = 10  # Identifier\nif True: pass  # Keyword"
        item["working_steps"] = [
            "Interpreter parses source code text into syntax tokens",
            "Filters out comments and docstring blocks from execution",
            "Validates user-defined identifiers against naming rules",
            "Maps identifiers and reserves keywords in the symbol table"
        ]
        item["code_basic"] = "import keyword\nprint('Is \"if\" a keyword?', keyword.iskeyword('if'))\nprint('Is \"var\" a keyword?', keyword.iskeyword('var'))"
        item["code_basic_out"] = "Is \"if\" a keyword? True\nIs \"var\" a keyword? False"
        item["code_basic_highlights"] = [
            "Imports the standard keyword module in Python",
            "Uses keyword.iskeyword() to check if 'if' is a reserved word",
            "Checks if user identifier name 'var' is a keyword"
        ]
        item["code_complex"] = "import keyword\nkw_list = keyword.kwlist\nprint('Total keywords:', len(kw_list))\nprint('First 5 keywords:', kw_list[:5])"
        item["code_complex_out"] = "Total keywords: 35\nFirst 5 keywords: ['False', 'None', 'True', 'and', 'as']"
        item["code_complex_highlights"] = [
            "Imports the standard keyword library",
            "Retrieves full sequence of reserved words using kwlist",
            "Outputs count and lists first five alphabetical keywords"
        ]
        item["mistakes"] = [
            "Attempting to reassign or use keywords as variable names (raises SyntaxError)",
            "Beginning identifiers with digits or using hyphens in variable names"
        ]
        item["best_practices"] = [
            "Follow snake_case conventions for variable names and camelCase for class names",
            "Do not write comments that describe what the code does; write comments explaining why"
        ]
        item["applications"] = [
            "Syntax highlighting in text editors and IDEs",
            "Static analysis and code linter checks",
            "Code compilation and token parsing flows"
        ]
        item["interview_q1"] = "What are keywords and how do they differ from identifiers?"
        item["interview_a1"] = "Keywords are reserved words predefined by Python to control syntax and execution flow (e.g. if, def). Identifiers are user-defined names given to variables, classes, or functions."
        item["interview_q2"] = "Why can keywords not be used as identifiers?"
        item["interview_a2"] = "Because the compiler/interpreter maps keywords to specific structural operations. Reassigning them would conflict with code execution syntax rules."
        item["practice_q1"] = "Write a script that prints all active keywords alphabetically."
        item["practice_q2"] = "Write a validator script that checks if a user-supplied name is a valid identifier."
        item["quiz_q"] = "Which of the following is a valid Python identifier?"
        item["quiz_options"] = ["2var", "my-var", "import", "_my_var"]
        item["quiz_ans"] = "_my_var"
        item["quiz_explanation"] = "Identifiers must start with a letter or underscore and cannot contain hyphens or be reserved keywords. _my_var satisfies all identifier naming rules."
        item["comparison_table"] = {
            "headers": ["Component", "Definition", "Syntax / Form", "Interpretation", "Primary Rules"],
            "rows": [
                ["Comments", "Non-executable documentation notes", "# (inline) or ''' (block)", "Ignored by interpreter", "Should explain the intent, not just repeat the code"],
                ["Identifiers", "User-defined names for program variables/entities", "letters, digits, underscore", "Resolved dynamically in scopes", "Must not start with a digit or use special symbols"],
                ["Keywords", "Reserved words with predefined syntax meanings", "if, else, for, True, None", "Defines the program control flow", "Cannot be used as variable names or reassigned"]
            ]
        }

# Make sure all 30 elements are inside COURSE_DATA
# Topic 1 to 11 are in COURSE_DATA already from the SYLLABUS_TOPICS list
# Let's write the execution loop to process them
def make_presentations():
    out_dir = os.path.abspath(".")
    
    for idx, data in enumerate(COURSE_DATA):
        prs = Presentation()
        prs.slide_width = Inches(13.333)
        prs.slide_height = Inches(7.5)
        
        # 1. Slide 1: Title Slide
        slide = SlideBuilder.create_title_slide(prs, data["title"], data["subtitle"])
        slide.notes_slide.notes_text_frame.text = generate_speaker_notes(data["title"], "Title Slide", "title", data)
        
        # 2. Slide 2: Learning Objectives
        obj_bullets = [
            "Understand the official definition of this topic.",
            "Analyze the syntax structures, characteristics, and operators.",
            "Write basic and complex Python code implementations.",
            "Review interview questions, coding traps, and practice assignments."
        ]
        slide = SlideBuilder.create_content_slide(prs, "Learning Objectives", obj_bullets, "Objectives", "This presentation covers all topics strictly mapped to the complete Python course curriculum.")
        slide.notes_slide.notes_text_frame.text = generate_speaker_notes(data["title"], "Learning Objectives", "objectives", data)
        
        # 3. Slide 3: Concept Definition
        intro_bullets = [
            "Core Definition: " + data["definition"],
            "Essential construct for building structured logic.",
            "Governed by the Python runtime execution specifications."
        ]
        slide = SlideBuilder.create_content_slide(prs, "Conceptual Overview", intro_bullets, "Definition", data["definition"])
        slide.notes_slide.notes_text_frame.text = generate_speaker_notes(data["title"], "Definition and Concept", "concepts", data)
        
        # 4. Slide 4: Key Features
        slide = SlideBuilder.create_content_slide(prs, "Key Characteristics", ["• " + f for f in data["features"]], "Features List", "These features establish how Python interprets and runs the logic.")
        slide.notes_slide.notes_text_frame.text = generate_speaker_notes(data["title"], "Key Features", "concepts", data)
        
        # 5. Slide 5: Advantages vs. Disadvantages
        slide = SlideBuilder.create_comparison_slide(prs, "Advantages vs. Disadvantages", "Key Advantages", data["advantages"], "Limitations & Tradeoffs", data["disadvantages"])
        slide.notes_slide.notes_text_frame.text = generate_speaker_notes(data["title"], "Advantages & Disadvantages", "advantages", data)
        
        # 5b. Slide 5b: Comparison Table (if exists)
        if data.get("comparison_table") is not None:
            slide = SlideBuilder.create_table_slide(
                prs, 
                "Built-in vs. User-defined Functions", 
                data["comparison_table"]["headers"], 
                data["comparison_table"]["rows"]
            )
            slide.notes_slide.notes_text_frame.text = generate_speaker_notes(
                data["title"], 
                "Built-in vs User-defined Comparison", 
                "concepts", 
                data
            )
        
        # 6. Slide 6: Syntax & Base Rules
        syntax_bullets = [
            "Syntactical structure is strict and defined.",
            "Requires correct indentation block configurations.",
            "Incorrect structure will raise a compile-time SyntaxError."
        ]
        slide = SlideBuilder.create_content_slide(prs, "Syntax and Conventions", syntax_bullets, "Syntax Block", data["syntax"])
        slide.notes_slide.notes_text_frame.text = generate_speaker_notes(data["title"], "Syntax Structure", "syntax", data)
        
        # 7. Slide 7: Working Diagram
        slide = SlideBuilder.create_diagram_slide(prs, "Interpreter Working Model", "flowchart", data["working_steps"])
        slide.notes_slide.notes_text_frame.text = generate_speaker_notes(data["title"], "Internal Processing Flow", "concepts", data)
        
        # 8. Slide 8: Basic Code Example + Key Highlights
        basic_hl = data.get("code_basic_highlights", ["Basic variable usage.", "Simple logical sequence.", "Direct console print outputs."])
        if "code_b_hl" in data:
            basic_hl = data["code_b_hl"]
        slide = SlideBuilder.create_code_slide(prs, "Basic Program Implementation", data["code_basic"], data["code_basic_out"], basic_hl)
        slide.notes_slide.notes_text_frame.text = generate_speaker_notes(data["title"], "Basic Code Example", "code", data)
        
        # 9. Slide 9: Complex Code Example + Key Highlights
        complex_hl = data.get("code_complex_highlights", ["Handles conditional values.", "Utilizes variable scopes.", "Demonstrates logical loops/returns."])
        if "code_c_hl" in data:
            complex_hl = data["code_c_hl"]
        slide = SlideBuilder.create_code_slide(prs, "Complex Program Implementation", data["code_complex"], data["code_complex_out"], complex_hl)
        slide.notes_slide.notes_text_frame.text = generate_speaker_notes(data["title"], "Complex Code Example", "code", data)
        
        # 10. Slide 10: Common Mistakes & Best Practices
        slide = SlideBuilder.create_comparison_slide(prs, "Common Mistakes vs Best Practices", "Mistakes (What to Avoid)", data["mistakes"], "Best Practices (What to Do)", data["best_practices"])
        slide.notes_slide.notes_text_frame.text = generate_speaker_notes(data["title"], "Common Errors", "mistakes", data)
        
        # 11. Slide 11: Real-World Applications
        slide = SlideBuilder.create_content_slide(prs, "Real-World Applications", ["• " + app for app in data["applications"]], "Application Scope", "Used globally to build automation and computer tools.")
        slide.notes_slide.notes_text_frame.text = generate_speaker_notes(data["title"], "Real-World Applications", "applications", data)
        
        # 12. Slide 12: Interview Q1 (Hidden State)
        slide = SlideBuilder.create_interview_question_slide(prs, data["title"], data["interview_q1"], 1)
        slide.notes_slide.notes_text_frame.text = generate_speaker_notes(data["title"], "Interview Q1 (Hidden)", "interview_q", {"interview_q": data["interview_q1"]})
        
        # 13. Slide 13: Interview Q1 (Revealed State)
        slide = SlideBuilder.create_interview_answer_slide(prs, data["title"], data["interview_q1"], data["interview_a1"], 1)
        slide.notes_slide.notes_text_frame.text = generate_speaker_notes(data["title"], "Interview Q1 (Revealed)", "interview_a", {"interview_q": data["interview_q1"]})
        
        # 14. Slide 14: Interview Q2 (Hidden State)
        slide = SlideBuilder.create_interview_question_slide(prs, data["title"], data["interview_q2"], 2)
        slide.notes_slide.notes_text_frame.text = generate_speaker_notes(data["title"], "Interview Q2 (Hidden)", "interview_q", {"interview_q": data["interview_q2"]})
        
        # 15. Slide 15: Interview Q2 (Revealed State)
        slide = SlideBuilder.create_interview_answer_slide(prs, data["title"], data["interview_q2"], data["interview_a2"], 2)
        slide.notes_slide.notes_text_frame.text = generate_speaker_notes(data["title"], "Interview Q2 (Revealed)", "interview_a", {"interview_q": data["interview_q2"]})
        
        # 16. Slide 16: Practical Coding Lab Exercise
        slide = SlideBuilder.create_content_slide(
            prs, 
            "Practical Coding Exercise", 
            [
                data["practice_q1"],
                "Task: Write the source code in your editor.",
                "Verify outputs using different inputs."
            ], 
            "Practice Task", 
            data["practice_q2"]
        )
        slide.notes_slide.notes_text_frame.text = generate_speaker_notes(data["title"], "Practical Coding Exercise", "code", {"interview_q": data["practice_q1"]})
        
        # 17. Slide 17: Interactive Quiz (Hidden State)
        slide = SlideBuilder.create_quiz_question_slide(prs, data["title"], data["quiz_q"], data["quiz_options"])
        slide.notes_slide.notes_text_frame.text = generate_speaker_notes(data["title"], "Quiz (Hidden)", "quiz_q", {"quiz_q": data["quiz_q"]})
        
        # 18. Slide 18: Interactive Quiz (Revealed State)
        quiz_exp = data.get("quiz_explanation", "This is the correct option based on standard execution rules.")
        slide = SlideBuilder.create_quiz_answer_slide(prs, data["title"], data["quiz_q"], data["quiz_options"], data["quiz_ans"], quiz_exp)
        slide.notes_slide.notes_text_frame.text = generate_speaker_notes(data["title"], "Quiz (Revealed)", "quiz_a", {"quiz_q": data["quiz_q"]})
        
        # 19. Slide 19: Module Summary & Reference Links
        slide = SlideBuilder.create_summary_slide(prs, "Module Summary & References", data["summary_points"], data["references"])
        slide.notes_slide.notes_text_frame.text = generate_speaker_notes(data["title"], "Summary & References", "summary", data)
        
        # Save presentation in the workspace root, with backup fallback if file is locked
        target_path = os.path.join(out_dir, data["filename"])
        try:
            prs.save(target_path)
            print(f"[{idx+1}/30] Generated: {target_path} | Slides: {len(prs.slides)}")
        except PermissionError:
            backup_dir = os.path.abspath("backup_presentations")
            os.makedirs(backup_dir, exist_ok=True)
            backup_path = os.path.join(backup_dir, data["filename"])
            prs.save(backup_path)
            print(f"[{idx+1}/30] Warning: File was locked. Saved backup in: {backup_path} | Slides: {len(prs.slides)}")

if __name__ == "__main__":
    make_presentations()
