import os
import sys
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

# Theme Colors (Matching other decks in the course)
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
            
            # Format bullets with bold prefixes
            if ":" in bullet:
                parts = bullet.split(":", 1)
                p.text = ""
                run_bold = p.add_run()
                run_bold.text = parts[0] + ":"
                run_bold.font.bold = True
                run_bold.font.name = 'Calibri'
                run_bold.font.size = Pt(18)
                run_bold.font.color.rgb = TEXT_PRIMARY
                
                run_normal = p.add_run()
                run_normal.text = parts[1]
                run_normal.font.name = 'Calibri'
                run_normal.font.size = Pt(18)
                run_normal.font.color.rgb = TEXT_PRIMARY
            else:
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
            p.font.name = 'Calibri'
            p.font.size = Pt(14)
            p.font.color.rgb = TEXT_PRIMARY
            p.space_after = Pt(6)
            
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
        notes_body = f"Let's review the main advantages. Using this construct provides benefits like modularity, clean scope isolation, and code reuse. However, there are limitations to keep in mind, specifically function call overhead and execution stack limits. Knowing these limitations helps us write better and more optimized code."
    elif slide_type == 'syntax':
        notes_body = f"Here is the standard syntax. Notice how the keyword is placed at the start, followed by appropriate parameters and concluding with a colon. Since Python uses indentation to represent execution blocks rather than curly braces, you must be extremely consistent with your spacing. In your code, always use 4 spaces for cleaner structure."
    elif slide_type == 'code':
        notes_body = f"Now, let's analyze the code implementation. Look at the slate-colored code editor box on the left. We declare our variables and use the structure. When we execute this script, the PVM runs it line-by-line and generates the output shown in the terminal console box. Notice how the logic handles basic and edge cases without runtime errors."
    elif slide_type == 'mistakes':
        notes_body = f"In coding exercises, learners often make mistakes such as forgetting the trailing colon or using wrong scopes. To prevent this, implement the best practices. Keep names descriptive, write simple modular lines, and insert docstrings for documentation. This ensures your script is clean and maintainable."
    elif slide_type == 'applications':
        notes_body = f"In industry, these principles are used to design solid applications. For example, reusable APIs, automation scripts, and ML data steps rely heavily on these mechanisms. As Python learners, practicing these logic flows will build the technical foundation needed for coding interviews and software engineering jobs."
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

# Content details for "Final Course Annexure" presentation
DATA = {
    "title": "Python Final Course Annexure",
    "filename": "Final_Course_Annexure.pptx",
    "subtitle": "Course Summary, Syntax Standards, and Reusable Reference Sheets",
    "definition": "The Final Course Annexure is a central compilation of syntax cheatsheets, style conventions, standard package architectures, and built-in exception hierarchies designed as a developer resource.",
    
    "features": [
        "PEP 8 Standards: Standardizes styling layout rules including snake_case naming and 4-space indentations.",
        "Module Hierarchies: Outlines project folder layout setups, matching modular packaging standards.",
        "Built-in Exceptions: Explains exception handling hierarchy paths for easy syntax references.",
        "Lifelong Reference: Functions as a consolidated central developer index, replacing loose documentation."
    ],
    
    "advantages": [
        "Time Efficiency: Consolidates common syntax structures into one search area, saving reference time.",
        "Consistent Formatting: Enforces standardized style rules across all files in your coding repository.",
        "Dependency Isolation: Prevents libraries naming clashes using structured packages and scopes.",
        "Standard Checklist: Provides a central check guide before merging code to production branches."
    ],
    "disadvantages": [
        "Maintenance Cost: Requires regular updates when language features or framework version releases change.",
        "Lookup Overload: Can be verbose if too many minor API syntax definitions are appended."
    ],
    
    "syntax": "# Setup local virtual environment:\npython -m venv .venv\n\n# Activation commands:\n.venv\\Scripts\\activate  # Windows\nsource .venv/bin/activate  # macOS/Linux",
    "working_steps": [
        "Cache: Check sys.modules cache to verify if module is already loaded",
        "Standards: Search standard library core modules and built-ins directories",
        "sys.path: Scan sys.path directory paths sequentially for matching filename",
        "Load: PVM compiles source code to bytecode and executes block namespace"
    ],
    
    "code_basic": "import os\nimport sys\n\ndef show_environment():\n    \"\"\"Prints current workspace path and Python interpreter version.\"\"\"\n    print(\"Active Workspace:\", os.path.basename(os.path.abspath(\".\")))\n    print(\"Interpreter Executable:\", os.path.basename(sys.executable))\n\nif __name__ == \"__main__\":\n    show_environment()",
    "code_basic_out": "Active Workspace: ffmpeg-8.1.2-essentials_build\nInterpreter Executable: python.exe",
    "code_basic_hl": [
        "Imports standard os and sys modules",
        "Declares utility function show_environment with docstring",
        "Uses os.path methods to print root folder name",
        "Uses entry point guard to run print statements only when executed"
    ],
    
    "code_complex": "import time\nfrom typing import Iterator\n\nclass TimerContext:\n    \"\"\"Context manager measuring block execution time.\"\"\"\n    def __init__(self, description: str):\n        self.description = description\n        self.start_time = 0.0\n\n    def __enter__(self):\n        self.start_time = time.perf_counter()\n        return self\n\n    def __exit__(self, exc_type, exc_val, exc_tb):\n        elapsed = time.perf_counter() - self.start_time\n        print(f\"[{self.description}] Elapsed: {elapsed:.4f}s\")\n\ndef count_numbers(limit: int) -> Iterator[int]:\n    \"\"\"Yields integers up to limit using type hints.\"\"\"\n    for val in range(1, limit + 1):\n        yield val\n\nwith TimerContext(\"Sum Numbers\"):\n    total = sum(count_numbers(10000))\n    print(\"Calculated Sum:\", total)",
    "code_complex_out": "Calculated Sum: 50005000\n[Sum Numbers] Elapsed: 0.0008s",
    "code_complex_hl": [
        "Declares context manager using __enter__ and __exit__ methods",
        "Measures block elapsed time using high-precision performance counter",
        "Implements generator function count_numbers using yield keyword",
        "Demonstrates context with sum of generator integers and logs runtime"
    ],
    
    "mistakes": [
        "Polluting global namespaces using wildcard imports: from module import *.",
        "Naming custom python scripts identical to standard libraries (e.g. random.py).",
        "Declaring mutable objects (like lists/dicts) directly as default arguments.",
        "Attempting to install module dependencies without activating virtual environment."
    ],
    "best_practices": [
        "Write explicit imports: from module import name to improve read clarity.",
        "Enforce PEP 8 style formatting strictly in all project source codes.",
        "Always freeze library dependencies to file using: pip freeze > requirements.txt.",
        "Wrap execution scripts in main entry guards: if __name__ == '__main__':."
    ],
    
    "applications": [
        "Structuring modular layouts for distribution packages on PyPI.",
        "Designing enterprise-level directory templates for software teams.",
        "Standardizing build automation routines and deployment pipelines.",
        "Managing workspace environment settings and credential configurations."
    ],
    
    "comparison_table": {
        "headers": ["Feature / Aspect", "Course Annexure Sheets", "Raw Web Searches"],
        "rows": [
            ["Search Speed", "Near-instant; local cheatsheet is structured for syllabus.", "Slow; requires filtering through unrelated forums or SEO logs."],
            ["Data Relevance", "Guaranteed to match course version and execution environment.", "Unpredictable; may show legacy Python 2 or obsolete APIs."],
            ["Code Consistency", "Enforces standard layouts and formats for coursework.", "No consistency; styles vary wildly across different sites."],
            ["Syntax Verification", "All code examples are verified executable in local venv.", "Untested snippets can raise syntax or package import errors."]
        ]
    },
    
    "interview_q1": "What is the difference between relative imports and absolute imports in Python?",
    "interview_a1": "Absolute imports specify the full path to a module starting from the project's root folder, which is readable and robust (e.g. import pkg.module). Relative imports use dot notation to import relative to the current module's file location (e.g. from . import module), which is useful inside self-contained packages.",
    
    "interview_q2": "What are the rules and lookup steps for scope resolution under the LEGB rule?",
    "interview_a2": "The LEGB rule stands for Local, Enclosing, Global, and Built-in scopes. When searching for a variable name, Python looks through these namespaces in strict order. If the identifier is not found in any of these four concentric scopes, Python raises a NameError runtime exception.",
    
    "practice_q1": "Create a custom exception class ConfigError and write a loader function that raises it if a file is missing.",
    "practice_q2": "Write a script that inspects sys.path and prints the absolute path of each folder on a separate line.",
    
    "quiz_q": "Which interpreter list variable contains the folder search paths scanned during import statements?",
    "quiz_options": ["sys.paths", "sys.path", "os.path", "builtins.paths"],
    "quiz_ans": "sys.path",
    "quiz_explanation": "The sys.path variable is a standard list of string directories that Python scans sequentially to search for and load modules.",
    
    "summary_points": [
        "Mastered project structure standards, packages layouts, and virtual environments.",
        "Learned import search pathways, sys.path lookups, and the LEGB scope rules.",
        "Implemented context managers, custom exceptions, and performance measuring scripts.",
        "Consolidated PEP 8 rules, common coding traps, and interview prep questions."
    ],
    "references": [
        "PEP 8 - Style Guide for Python Code (peps.python.org/pep-0008/)",
        "Python Tutorial - Modules and Packages (docs.python.org/3/tutorial/modules.html)",
        "PEP 370 - Per user site-packages directory specification"
    ]
}

def make_presentation():
    out_dir = os.path.abspath(".")
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    
    # 1. Slide 1: Title Slide
    slide = SlideBuilder.create_title_slide(prs, DATA["title"], DATA["subtitle"])
    slide.notes_slide.notes_text_frame.text = generate_speaker_notes(DATA["title"], "Title Slide", "title", DATA)
    
    # 2. Slide 2: Learning Objectives
    obj_bullets = [
        "Review project layouts, package directories, and namespace structures.",
        "Analyze sys.path lookup models and LEGB namespace resolution rules.",
        "Implement virtual environments and requirements file configurations.",
        "Analyze context managers, type hints, and yield generator loops.",
        "Review interview preparations, mistakes list, and cheat sheet links."
    ]
    slide = SlideBuilder.create_content_slide(prs, "Learning Objectives", obj_bullets, "Objectives", "This presentation serves as the final annexure and syntax review guide for the complete Python curriculum.")
    slide.notes_slide.notes_text_frame.text = generate_speaker_notes(DATA["title"], "Learning Objectives", "objectives", DATA)
    
    # 3. Slide 3: Conceptual Overview
    intro_bullets = [
        "Core Definition: " + DATA["definition"],
        "Syllabus Indexing: Consolidated reference of language specs, execution paths, and style guides.",
        "Practical Standard: Enforces architectural rules for modular, scalable, and team-based coding."
    ]
    slide = SlideBuilder.create_content_slide(prs, "Conceptual Overview", intro_bullets, "Definition", DATA["definition"])
    slide.notes_slide.notes_text_frame.text = generate_speaker_notes(DATA["title"], "Definition and Concept", "concepts", DATA)
    
    # 4. Slide 4: Key Characteristics
    slide = SlideBuilder.create_content_slide(prs, "Key Characteristics", ["• " + f for f in DATA["features"]], "Features List", "These features establish the coding standard rules for pythonic code structure.")
    slide.notes_slide.notes_text_frame.text = generate_speaker_notes(DATA["title"], "Key Features", "concepts", DATA)
    
    # 5. Slide 5: Advantages vs. Disadvantages (Comparison Table)
    slide = SlideBuilder.create_table_slide(
        prs, 
        "Advantages vs. Disadvantages of Local Annexures", 
        DATA["comparison_table"]["headers"], 
        DATA["comparison_table"]["rows"]
    )
    slide.notes_slide.notes_text_frame.text = generate_speaker_notes(
        DATA["title"], 
        "Advantages & Disadvantages Table", 
        "advantages", 
        DATA
    )
    
    # 6. Slide 6: Syntax and Conventions
    syntax_bullets = [
        "Venv Creation: Use the venv core module to isolate project module versions.",
        "Activation Step: Activation modifies shell path parameters to prioritize the local bin/Scripts folder.",
        "Dependency Freeze: pip freeze writes active module libraries list to requirements files."
    ]
    slide = SlideBuilder.create_content_slide(prs, "Syntax and Conventions", syntax_bullets, "Venv Setup Block", DATA["syntax"])
    slide.notes_slide.notes_text_frame.text = generate_speaker_notes(DATA["title"], "Syntax and Conventions", "syntax", DATA)
    
    # 7. Slide 7: Interpreter Working Model (Flowchart Diagram)
    slide = SlideBuilder.create_diagram_slide(prs, "Interpreter Import Working Model", "flowchart", DATA["working_steps"])
    slide.notes_slide.notes_text_frame.text = generate_speaker_notes(DATA["title"], "Internal Import Flow", "concepts", DATA)
    
    # 8. Slide 8: Basic Program Implementation
    slide = SlideBuilder.create_code_slide(prs, "Basic Script: Workspace Inspector", DATA["code_basic"], DATA["code_basic_out"], DATA["code_basic_hl"])
    slide.notes_slide.notes_text_frame.text = generate_speaker_notes(DATA["title"], "Basic Code Implementation", "code", DATA)
    
    # 9. Slide 9: Complex Program Implementation
    slide = SlideBuilder.create_code_slide(prs, "Complex Script: Performance Timer Context", DATA["code_complex"], DATA["code_complex_out"], DATA["code_complex_hl"])
    slide.notes_slide.notes_text_frame.text = generate_speaker_notes(DATA["title"], "Complex Code Implementation", "code", DATA)
    
    # 10. Slide 10: Common Mistakes
    mistakes_bullets = [
        "Wildcard Imports: from module import * pollutes target namespace symbols.",
        "Name Collisions: naming scripts like random.py blocks importing core library.",
        "Mutable Defaults: setting defaults like lists/dicts causes shared list errors.",
        "Isolations Failures: installing package modules into global site-packages folder."
    ]
    slide = SlideBuilder.create_content_slide(prs, "Common Mistakes in Python Projects", mistakes_bullets, "Mistakes to Avoid", "These common traps can easily break compilation blocks and execution scopes.")
    slide.notes_slide.notes_text_frame.text = generate_speaker_notes(DATA["title"], "Common Mistakes", "mistakes", DATA)
    
    # 11. Slide 11: Best Practices
    best_practices_bullets = [
        "Explicit Imports: import module or from module import func is clean and readable.",
        "Formatting Guidelines: run linters and formatters to strictly enforce PEP 8 style guides.",
        "Freeze Dependencies: save version logs in requirements.txt file at project root.",
        "Scope Protections: wrap main routines inside __name__ == '__main__' execution guards."
    ]
    slide = SlideBuilder.create_content_slide(prs, "Best Practices & Guidelines", best_practices_bullets, "Coding Guidelines", "Following these structural guidelines guarantees codebase scalability and clean designs.")
    slide.notes_slide.notes_text_frame.text = generate_speaker_notes(DATA["title"], "Best Practices", "concepts", DATA)
    
    # 12. Slide 12: Real World Applications
    slide = SlideBuilder.create_content_slide(prs, "Real World Applications", ["• " + app for app in DATA["applications"]], "Application Scope", "These standard layouts are used globally to distribute open-source and commercial software.")
    slide.notes_slide.notes_text_frame.text = generate_speaker_notes(DATA["title"], "Real-World Applications", "applications", DATA)
    
    # 13. Slide 13: Interview Question 1 (Hidden State)
    slide = SlideBuilder.create_interview_question_slide(prs, DATA["title"], DATA["interview_q1"], 1)
    slide.notes_slide.notes_text_frame.text = generate_speaker_notes(DATA["title"], "Interview Q1 (Hidden)", "interview_q", {"interview_q": DATA["interview_q1"]})
    
    # 14. Slide 14: Interview Answer 1 (Revealed State)
    slide = SlideBuilder.create_interview_answer_slide(prs, DATA["title"], DATA["interview_q1"], DATA["interview_a1"], 1)
    slide.notes_slide.notes_text_frame.text = generate_speaker_notes(DATA["title"], "Interview Q1 (Revealed)", "interview_a", {"interview_q": DATA["interview_q1"]})
    
    # 15. Slide 15: Interview Question 2 (Hidden State)
    slide = SlideBuilder.create_interview_question_slide(prs, DATA["title"], DATA["interview_q2"], 2)
    slide.notes_slide.notes_text_frame.text = generate_speaker_notes(DATA["title"], "Interview Q2 (Hidden)", "interview_q", {"interview_q": DATA["interview_q2"]})
    
    # 16. Slide 16: Interview Answer 2 (Revealed State)
    slide = SlideBuilder.create_interview_answer_slide(prs, DATA["title"], DATA["interview_q2"], DATA["interview_a2"], 2)
    slide.notes_slide.notes_text_frame.text = generate_speaker_notes(DATA["title"], "Interview Q2 (Revealed)", "interview_a", {"interview_q": DATA["interview_q2"]})
    
    # 17. Slide 17: Practical Coding Exercise
    slide = SlideBuilder.create_content_slide(
        prs, 
        "Practical Coding Exercise", 
        [
            DATA["practice_q1"],
            "Task: Open your code editor and declare the custom exception class.",
            "Verify that raising it inside the load logic triggers correct handlers."
        ], 
        "Practice Lab", 
        DATA["practice_q2"]
    )
    slide.notes_slide.notes_text_frame.text = generate_speaker_notes(DATA["title"], "Practical Coding Exercise", "code", {"interview_q": DATA["practice_q1"]})
    
    # 18. Slide 18: Interactive Quiz (Hidden State)
    slide = SlideBuilder.create_quiz_question_slide(prs, DATA["title"], DATA["quiz_q"], DATA["quiz_options"])
    slide.notes_slide.notes_text_frame.text = generate_speaker_notes(DATA["title"], "Quiz (Hidden)", "quiz_q", {"quiz_q": DATA["quiz_q"]})
    
    # 19. Slide 19: Interactive Quiz (Revealed State)
    quiz_exp = DATA.get("quiz_explanation", "This is the correct option based on standard execution rules.")
    slide = SlideBuilder.create_quiz_answer_slide(prs, DATA["title"], DATA["quiz_q"], DATA["quiz_options"], DATA["quiz_ans"], quiz_exp)
    slide.notes_slide.notes_text_frame.text = generate_speaker_notes(DATA["title"], "Quiz (Revealed)", "quiz_a", {"quiz_q": DATA["quiz_q"]})
    
    # 20. Slide 20: Module Summary & Reference Links
    slide = SlideBuilder.create_summary_slide(prs, "Module Summary & References", DATA["summary_points"], DATA["references"])
    slide.notes_slide.notes_text_frame.text = generate_speaker_notes(DATA["title"], "Summary & References", "summary", DATA)
    
    # Save presentation
    target_path = os.path.join(out_dir, DATA["filename"])
    prs.save(target_path)
    print(f"Generated: {target_path} | Slides: {len(prs.slides)}")

if __name__ == "__main__":
    make_presentation()
