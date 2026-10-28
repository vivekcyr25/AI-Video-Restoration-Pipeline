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

# Complete slide deck details for Binary File Handling
DATA = {
    "title": "Python Binary File Handling",
    "filename": "20_Binary_File_Handling.pptx",
    "subtitle": "Data Persistence and Object Serialization using the Pickle Module",
    "definition": "Binary File Handling in Python involves reading and writing data in the raw byte format directly from and to storage, using serialization libraries like 'pickle' to preserve Python objects without character translation.",
    
    "features": [
        "Raw Byte Storage: Data is stored as a sequence of bytes (binary format) rather than human-readable text characters.",
        "Object Serialization: The pickle module converts Python object structures (lists, dicts) into byte streams (pickling).",
        "Reconstruction: The load() method reconstructs the serialized byte stream back into exact Python objects (unpickling).",
        "File Modes: Operates exclusively under binary modes including 'wb' (write binary), 'rb' (read binary), and 'ab' (append binary)."
    ],
    
    "advantages": [
        "Type Integrity: Preserves nested lists, tuples, and dictionaries directly, saving complex parsing logic.",
        "Performance: Direct memory-to-disk transfers are much faster than converting values to text format.",
        "Binary Obfuscation: Files are not human-readable in simple text editors, providing basic data protection.",
        "Compact Storage: Serialized binary formats can occupy less disk space compared to verbose text formatting."
    ],
    
    "disadvantages": [
        "Language Dependency: Pickle files are highly specific to Python and cannot be parsed easily by other programming languages.",
        "Security Risk: Unpickling untrusted files can execute arbitrary malicious code via exploitation of constructor hooks.",
        "Compatibility Limits: Pickled objects may fail to deserialize across major Python version releases."
    ],
    
    "syntax": "import pickle\npickle.dump(object, file_object)  # To write data\nobject = pickle.load(file_object)  # To read data",
    
    "working_steps": [
        "Open file in write-binary ('wb') or read-binary ('rb') mode",
        "Serialize Python object hierarchy using pickle.dump() wrapper",
        "De-serialize byte stream from disk using pickle.load() loader",
        "Close file stream cleanly using context manager or close() method"
    ],
    
    # Slides code content
    "code_basic_write": "import pickle\n\ndata = ['computer', 'history', 'accounts']\nwith open('bi.dat', 'wb') as f:\n    pickle.dump(data, f)\nprint('Data written successfully!')",
    "code_basic_write_out": "Data written successfully!",
    "code_basic_write_hl": [
        "Imports standard pickle library",
        "Opens 'bi.dat' in write-binary 'wb' mode",
        "Serializes and saves list using pickle.dump(object, file)"
    ],
    
    "code_basic_read": "import pickle\n\nwith open('bi.dat', 'rb') as f:\n    loaded_data = pickle.load(f)\nprint('Loaded:', loaded_data)",
    "code_basic_read_out": "Loaded: ['computer', 'history', 'accounts']",
    "code_basic_read_hl": [
        "Opens existing binary file in 'rb' mode",
        "Reads byte stream and reconstructs list via pickle.load(file)",
        "Prints exact structured list object directly"
    ],

    "code_user_write": "import pickle\n\nrecords = []\nwith open('bi.dat', 'wb') as f:\n    while True:\n        rno = int(input('Enter roll no: '))\n        name = input('Enter name: ')\n        marks = int(input('Enter marks: '))\n        records.append([rno, name, marks])\n        ch = input('Add more? (yes/no): ').lower()\n        if ch == 'no':\n            break\n    pickle.dump(records, f)\nprint(f'Saved {len(records)} records.')",
    "code_user_write_out": "Enter roll no: 101\nEnter name: Shyam\nEnter marks: 90\nAdd more? (yes/no): no\nSaved 1 records.",
    "code_user_write_hl": [
        "Declares empty list records to accumulate inputs",
        "Collects integer, string, and integer inputs inside loop",
        "Appends entries as nested lists [rno, name, marks]",
        "Saves entire nested collection in a single pickle.dump() call"
    ],

    "code_search_eq": "import pickle\n\ndef search_student(sid):\n    with open('abc.dat', 'rb') as f:\n        records = pickle.load(f)\n    found = False\n    for student in records:\n        if student[0] == sid:\n            print('Record Found:', student)\n            found = True\n            break\n    if not found:\n        print('Record not found.')\n\n# Example execution trace below",
    "code_search_eq_out": "Record Found: [101, 'Shyam', 90]",
    "code_search_eq_hl": [
        "Opens database file and loads nested records",
        "Iterates through elements representing individual student records",
        "Checks student[0] (Student ID) against query sid",
        "Prints record and flags found to terminate search"
    ],

    "code_search_range": "import pickle\n\ndef filter_cricketers():\n    with open('abc.dat', 'rb') as f:\n        cricketers = pickle.load(f)\n    found = False\n    for player in cricketers:\n        # Check if runs (index 2) > 10000\n        if player[2] > 10000:\n            print(f'Player: {player[0]} | Country: {player[1]} | Runs: {player[2]}')\n            found = True\n    if not found:\n        print('No cricketer found in this range.')",
    "code_search_range_out": "Player: Sachin | Country: India | Runs: 18426",
    "code_search_range_hl": [
        "Loads list of cricketers from binary file",
        "Applies greater-than filter comparison on index 2 (Runs)",
        "Iterates over all matches and prints formatted summary",
        "Prints fallback message if no player crossed threshold"
    ],

    "code_transfer_eof": "import pickle\n\ndef transfer_employees():\n    try:\n        with open('emp.dat', 'rb') as f_in, open('sample.dat', 'wb') as f_out:\n            employees = pickle.load(f_in)\n            # Filter male employees (gender at index 3)\n            filtered = [emp for emp in employees if emp[3] == 'm']\n            pickle.dump(filtered, f_out)\n            print(f'Transferred {len(filtered)} records.')\n    except FileNotFoundError:\n        print('Source file emp.dat not found.')\n    except EOFError:\n        print('EOFError handled: file empty or corrupted.')",
    "code_transfer_eof_out": "Transferred 12 records.",
    "code_transfer_eof_hl": [
        "Uses double context manager to open input/output binary streams",
        "Performs list comprehension filtering by gender code",
        "Handles FileNotFoundError for robust file presence checking",
        "Handles EOFError to safely handle empty or reading limits"
    ],
    
    "mistakes": [
        "Opening binary files using 'w' or 'r' mode instead of 'wb' or 'rb' (raises TypeError on write).",
        "Reversing parameters order: writing pickle.dump(file, obj) instead of pickle.dump(obj, file).",
        "Failing to catch EOFError when trying to load from empty or newly-created files.",
        "Incorrect index offsets: accessing index values like student[3] without verifying records length."
    ],
    
    "best_practices": [
        "Always use context managers (with open) to guarantee file handles close on errors.",
        "Perform file presence verification using path.exists() before initiating read loads.",
        "Model data structures using dictionaries or custom classes instead of raw indexes for safer updates."
    ],
    
    "applications": [
        "Saving machine learning model states and hyperparameters (pickle/joblib).",
        "Caching heavy computing results on local disk to speed up subsequent executions.",
        "Saving game progress, player configurations, and inventories in local files.",
        "Serializing session states and database credentials in network protocols."
    ],
    
    "comparison_table": {
        "headers": ["Feature", "Text Files", "Binary Files"],
        "rows": [
            ["Storage Format", "ASCII/Unicode text characters", "Raw bytes (exact memory representation)"],
            ["File Mode", "w, r, a, w+, r+, a+", "wb, rb, ab, wb+, rb+, ab+"],
            ["Conversion", "Required (values translated to string characters)", "No conversion (objects dumped directly as byte streams)"],
            ["Data Integrity", "Limited to text strings; requires manual parsing", "Preserves nested lists, tuples, and dictionaries directly"],
            ["Performance", "Slower due to character translation overhead", "Faster (direct disk-to-memory block transfers)"],
            ["Line Endings", "Converts newlines based on OS default (\\n vs \\r\\n)", "No newline processing occurs; writes bytes exactly"]
        ]
    },
    
    "interview_q1": "What is pickling and unpickling in Python? Why is it useful?",
    "interview_a1": "Pickling is the process of converting Python object hierarchies into byte streams, and unpickling is the inverse. It is useful for serializing data structures (lists, dicts) to disk or sending them across networks without manual formatting.",
    
    "interview_q2": "What are the security implications of using the pickle module?",
    "interview_a2": "The pickle module is not secure. Deserializing data from untrusted sources can execute arbitrary python code by exploiting the __reduce__ method. Always use JSON, Protocol Buffers, or cryptographically signed pickles for untrusted inputs.",
    
    "practice_q1": "Write a program that manages an employee database (employee.dat) by providing options to: (1) Add employee records, (2) Search for an employee by ID, and (3) Update an employee's salary.",
    "practice_q2": "Create a script that splits a binary file containing student records into two separate binary files based on whether their marks are above or below 50.",
    
    "quiz_q": "Which mode should be used to append new binary data to an existing binary file?",
    "quiz_options": ["'a'", "'ab'", "'wb'", "'rb+'"],
    "quiz_ans": "'ab'",
    "quiz_explanation": "'ab' opens a file in append-binary mode, writing data at the end of the file without overwriting existing content.",
    
    "summary_points": [
        "Learned differences between text and binary files.",
        "Mastered pickling and unpickling of complex data structures.",
        "Implemented record searches, filters, and transfers.",
        "Explored EOFError safe handling and security practices."
    ],
    "references": [
        "Python official documentation: pickle module (docs.python.org/3/library/pickle.html)",
        "Core Python Programming Guide: Chapter on File Operations",
        "PEP 3118 - Revised Buffer Protocol specifications"
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
        "Understand the official definition of this topic.",
        "Analyze the syntax structures, characteristics, and operators.",
        "Write basic and complex Python code implementations.",
        "Review interview questions, coding traps, and practice assignments."
    ]
    slide = SlideBuilder.create_content_slide(prs, "Learning Objectives", obj_bullets, "Objectives", "This presentation covers all topics strictly mapped to the complete Python course curriculum.")
    slide.notes_slide.notes_text_frame.text = generate_speaker_notes(DATA["title"], "Learning Objectives", "objectives", DATA)
    
    # 3. Slide 3: Concept Definition
    intro_bullets = [
        "Core Definition: " + DATA["definition"],
        "Essential construct for building structured logic.",
        "Governed by the Python runtime execution specifications."
    ]
    slide = SlideBuilder.create_content_slide(prs, "Conceptual Overview", intro_bullets, "Definition", DATA["definition"])
    slide.notes_slide.notes_text_frame.text = generate_speaker_notes(DATA["title"], "Definition and Concept", "concepts", DATA)
    
    # 4. Slide 4: Key Features
    slide = SlideBuilder.create_content_slide(prs, "Key Characteristics", ["• " + f for f in DATA["features"]], "Features List", "These features establish how Python interprets and runs the logic.")
    slide.notes_slide.notes_text_frame.text = generate_speaker_notes(DATA["title"], "Key Features", "concepts", DATA)
    
    # 5. Slide 5: Advantages vs. Disadvantages
    slide = SlideBuilder.create_comparison_slide(prs, "Advantages vs. Disadvantages", "Key Advantages", DATA["advantages"], "Limitations & Tradeoffs", DATA["disadvantages"])
    slide.notes_slide.notes_text_frame.text = generate_speaker_notes(DATA["title"], "Advantages & Disadvantages", "advantages", DATA)
    
    # 6. Slide 6: Comparison Table
    slide = SlideBuilder.create_table_slide(
        prs, 
        "Text Files vs. Binary Files", 
        DATA["comparison_table"]["headers"], 
        DATA["comparison_table"]["rows"]
    )
    slide.notes_slide.notes_text_frame.text = generate_speaker_notes(
        DATA["title"], 
        "Text vs. Binary Comparison Table", 
        "concepts", 
        DATA
    )
    
    # 7. Slide 7: Syntax & Base Rules
    syntax_bullets = [
        "Syntactical structure is strict and defined.",
        "Requires correct indentation block configurations.",
        "Incorrect structure will raise a compile-time SyntaxError."
    ]
    slide = SlideBuilder.create_content_slide(prs, "Syntax and Conventions", syntax_bullets, "Syntax Block", DATA["syntax"])
    slide.notes_slide.notes_text_frame.text = generate_speaker_notes(DATA["title"], "Syntax Structure", "syntax", DATA)
    
    # 8. Slide 8: Interpreter Working Model (Flowchart Diagram)
    slide = SlideBuilder.create_diagram_slide(prs, "Interpreter Working Model", "flowchart", DATA["working_steps"])
    slide.notes_slide.notes_text_frame.text = generate_speaker_notes(DATA["title"], "Internal Processing Flow", "concepts", DATA)
    
    # 9. Slide 9: Basic Code Example — Writing Data
    slide = SlideBuilder.create_code_slide(prs, "Writing Data to Binary Files", DATA["code_basic_write"], DATA["code_basic_write_out"], DATA["code_basic_write_hl"])
    slide.notes_slide.notes_text_frame.text = generate_speaker_notes(DATA["title"], "Basic Writing Example", "code", DATA)
    
    # 10. Slide 10: Basic Code Example — Reading Data
    slide = SlideBuilder.create_code_slide(prs, "Reading Data from Binary Files", DATA["code_basic_read"], DATA["code_basic_read_out"], DATA["code_basic_read_hl"])
    slide.notes_slide.notes_text_frame.text = generate_speaker_notes(DATA["title"], "Basic Reading Example", "code", DATA)
    
    # 11. Slide 11: Complex Code Example — User-Driven Nested Records
    slide = SlideBuilder.create_code_slide(prs, "User-Driven Nested Records Writing", DATA["code_user_write"], DATA["code_user_write_out"], DATA["code_user_write_hl"])
    slide.notes_slide.notes_text_frame.text = generate_speaker_notes(DATA["title"], "Nested Write Example", "code", DATA)
    
    # 12. Slide 12: Complex Code Example — Searching Records (Equality)
    slide = SlideBuilder.create_code_slide(prs, "Searching Nested Records (Exact ID)", DATA["code_search_eq"], DATA["code_search_eq_out"], DATA["code_search_eq_hl"])
    slide.notes_slide.notes_text_frame.text = generate_speaker_notes(DATA["title"], "Record Searching Example", "code", DATA)

    # 13. Slide 13: Complex Code Example — Searching Records (Range filter)
    slide = SlideBuilder.create_code_slide(prs, "Searching Nested Records (Numeric Range)", DATA["code_search_range"], DATA["code_search_range_out"], DATA["code_search_range_hl"])
    slide.notes_slide.notes_text_frame.text = generate_speaker_notes(DATA["title"], "Range Filter Example", "code", DATA)

    # 14. Slide 14: Complex Code Example — File Transfer & EOFError Handling
    slide = SlideBuilder.create_code_slide(prs, "Data Transfer & EOFError Handling", DATA["code_transfer_eof"], DATA["code_transfer_eof_out"], DATA["code_transfer_eof_hl"])
    slide.notes_slide.notes_text_frame.text = generate_speaker_notes(DATA["title"], "File Transfer and EOF Example", "code", DATA)
    
    # 15. Slide 15: Common Mistakes & Best Practices
    slide = SlideBuilder.create_comparison_slide(prs, "Common Mistakes vs Best Practices", "Mistakes (What to Avoid)", DATA["mistakes"], "Best Practices (What to Do)", DATA["best_practices"])
    slide.notes_slide.notes_text_frame.text = generate_speaker_notes(DATA["title"], "Common Errors", "mistakes", DATA)
    
    # 16. Slide 16: Real-World Applications
    slide = SlideBuilder.create_content_slide(prs, "Real-World Applications", ["• " + app for app in DATA["applications"]], "Application Scope", "Used globally to build automation and computer tools.")
    slide.notes_slide.notes_text_frame.text = generate_speaker_notes(DATA["title"], "Real-World Applications", "applications", DATA)
    
    # 17. Slide 17: Interview Q1 (Hidden State)
    slide = SlideBuilder.create_interview_question_slide(prs, DATA["title"], DATA["interview_q1"], 1)
    slide.notes_slide.notes_text_frame.text = generate_speaker_notes(DATA["title"], "Interview Q1 (Hidden)", "interview_q", {"interview_q": DATA["interview_q1"]})
    
    # 18. Slide 18: Interview Q1 (Revealed State)
    slide = SlideBuilder.create_interview_answer_slide(prs, DATA["title"], DATA["interview_q1"], DATA["interview_a1"], 1)
    slide.notes_slide.notes_text_frame.text = generate_speaker_notes(DATA["title"], "Interview Q1 (Revealed)", "interview_a", {"interview_q": DATA["interview_q1"]})
    
    # 19. Slide 19: Interview Q2 (Hidden State)
    slide = SlideBuilder.create_interview_question_slide(prs, DATA["title"], DATA["interview_q2"], 2)
    slide.notes_slide.notes_text_frame.text = generate_speaker_notes(DATA["title"], "Interview Q2 (Hidden)", "interview_q", {"interview_q": DATA["interview_q2"]})
    
    # 20. Slide 20: Interview Q2 (Revealed State)
    slide = SlideBuilder.create_interview_answer_slide(prs, DATA["title"], DATA["interview_q2"], DATA["interview_a2"], 2)
    slide.notes_slide.notes_text_frame.text = generate_speaker_notes(DATA["title"], "Interview Q2 (Revealed)", "interview_a", {"interview_q": DATA["interview_q2"]})
    
    # 21. Slide 21: Practical Coding Lab Exercise
    slide = SlideBuilder.create_content_slide(
        prs, 
        "Practical Coding Exercise", 
        [
            DATA["practice_q1"],
            "Task: Write the source code in your editor.",
            "Verify outputs using different inputs."
        ], 
        "Practice Task", 
        DATA["practice_q2"]
    )
    slide.notes_slide.notes_text_frame.text = generate_speaker_notes(DATA["title"], "Practical Coding Exercise", "code", {"interview_q": DATA["practice_q1"]})
    
    # 22. Slide 22: Interactive Quiz (Hidden State)
    slide = SlideBuilder.create_quiz_question_slide(prs, DATA["title"], DATA["quiz_q"], DATA["quiz_options"])
    slide.notes_slide.notes_text_frame.text = generate_speaker_notes(DATA["title"], "Quiz (Hidden)", "quiz_q", {"quiz_q": DATA["quiz_q"]})
    
    # 23. Slide 23: Interactive Quiz (Revealed State)
    quiz_exp = DATA.get("quiz_explanation", "This is the correct option based on standard execution rules.")
    slide = SlideBuilder.create_quiz_answer_slide(prs, DATA["title"], DATA["quiz_q"], DATA["quiz_options"], DATA["quiz_ans"], quiz_exp)
    slide.notes_slide.notes_text_frame.text = generate_speaker_notes(DATA["title"], "Quiz (Revealed)", "quiz_a", {"quiz_q": DATA["quiz_q"]})
    
    # 24. Slide 24: Module Summary & Reference Links
    slide = SlideBuilder.create_summary_slide(prs, "Module Summary & References", DATA["summary_points"], DATA["references"])
    slide.notes_slide.notes_text_frame.text = generate_speaker_notes(DATA["title"], "Summary & References", "summary", DATA)
    
    # Save presentation
    target_path = os.path.join(out_dir, DATA["filename"])
    prs.save(target_path)
    print(f"Generated: {target_path} | Slides: {len(prs.slides)}")

if __name__ == "__main__":
    make_presentation()
