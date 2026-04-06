"""
seed_enneagram.py
Seeds 125 Enneagram personality questions with a 5-point Likert scale.
Scale: Strongly Disagree / Disagree / Neutral / Agree / Strongly Agree

Run from the project root with the virtual environment active:
    (.venv) PS Z:\\projects\\Psycho\\psycho_one> python backend/seed_enneagram.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import SessionLocal
from backend import models


# (text, subtest) — extracted from enneagram_questions.txt
QUESTIONS = [
    ("Critical of myself (my own worst critic) and find it easy to be judgmental and critical of other people as well.", "E1"),
    ("Believe that rules, regulations, policies, and procedures have a purpose and should be followed and I'm frustrated when others break rules.", "E1"),
    ("Value being well organized and punctual in myself and others.", "E1"),
    ("Motivated by the need to be correct, fair, and self-disciplined.", "E1"),
    ("Have a strong sense of right and wrong and strive for perfection.", "E1"),
    ("Easily discern what is wrong in a situation and how it could be done better.", "E1"),
    ("Do not consider being a perfectionist a negative thing and like to make sure all the details are just right.", "E1"),
    ("Personal integrity is extremely important to me.", "E1"),
    ("Manners and good taste are extremely important to me.", "E1"),
    ("Routine and structure help me stay focused and accomplish things.", "E1"),
    ("I'm extremely protective of my loved ones and feel good about helping the underdog.", "E2"),
    ("Listen patiently and can be very understanding and comforting to friends.", "E2"),
    ("Have a strong need to be noticed, liked, and appreciated for what I do for others.", "E2"),
    ("Like people to depend on me and deliver on my promises.", "E2"),
    ("Believe that my motives for helping others are noble and helpful.", "E2"),
    ("I'm told I'm a \"nice person\" and dislike putting myself first.", "E2"),
    ("Motivated by the need to be appreciated, loved, and connected to people.", "E2"),
    ("Need to feel close to people and feel rejected and hurt if I don't experience that closeness.", "E2"),
    ("I often sense what others need before they ask for it.", "E2"),
    ("I find it hard to say no when someone asks for my help.", "E2"),
    ("I feel most fulfilled when I am taking care of someone I love.", "E2"),
    ("I tend to give advice even when people have not asked for it.", "E2"),
    ("I sometimes feel resentful when my efforts go unnoticed or unappreciated.", "E2"),
    ("I naturally take on the role of caregiver in my relationships.", "E2"),
    ("Work hard and know how to get things done.", "E3"),
    ("To impress, I may take on too much and make promises I can't keep.", "E3"),
    ("Value exceeding standards and rising to the top of my profession.", "E3"),
    ("Value looking good, presenting a good first impression, and \"dressing for success.\"", "E3"),
    ("Believe that negative feelings are an obstacle to getting the job done.", "E3"),
    ("Tend to be idealistic and ambitious and want to contribute something positive to the world.", "E3"),
    ("Love to work and be productive, and work has tended to be a top priority in my life.", "E3"),
    ("Have been goal-oriented for as long as I can remember.", "E3"),
    ("I tend to adjust my personality depending on who I am trying to impress.", "E3"),
    ("Failure is something I find very difficult to accept about myself.", "E3"),
    ("I am very aware of how I am perceived by others in professional settings.", "E3"),
    ("I measure my self-worth largely by my achievements and accomplishments.", "E3"),
    ("I find it uncomfortable to slow down and do nothing productive.", "E3"),
    ("I tend to compare my progress and success to those around me.", "E3"),
    ("Creative and have an artistic view of life.", "E4"),
    ("Thrive in environments where I can express my creativity.", "E4"),
    ("Can be deeply hurt by the slightest criticism.", "E4"),
    ("Tend to be romantic and long for the great love of my life to come along.", "E4"),
    ("Feel different from others, as if \"on the outside looking in.\"", "E4"),
    ("Strive to be unique and have done things to avoid being ordinary.", "E4"),
    ("Can be caught in a fantasy world of romance and imagination.", "E4"),
    ("Tend to experience more melancholy than most people I know.", "E4"),
    ("Attracted to what is intense and out of the ordinary.", "E4"),
    ("Feel that something is missing in my life.", "E4"),
    ("Feel envious of other people's relationships, lifestyles, and accomplishments.", "E4"),
    ("Enjoy having elegant, refined, unique things that no one else has.", "E4"),
    ("I am drawn to art, music, or literature that expresses deep emotion or suffering.", "E4"),
    ("I sometimes idealize the past or mourn opportunities I feel I have missed.", "E4"),
    ("Tend to be more logical than emotional.", "E5"),
    ("Enjoy having control of my own time and private space.", "E5"),
    ("Enjoy the sense of independence that comes from living frugally.", "E5"),
    ("Prefer people not to know how I feel or what I think unless I tell them.", "E5"),
    ("May hesitate while I try to organize my thoughts and may not speak at all if I'm not comfortable with what I want to say.", "E5"),
    ("Can be critical, cynical, and argumentative and can act intellectually superior.", "E5"),
    ("Have ideas, theories, and opinions about almost everything.", "E5"),
    ("Have been told I am not in touch with my emotions.", "E5"),
    ("I feel uncomfortable around loud, emotional people.", "E5"),
    ("Enjoy spending time alone pursuing my personal interests.", "E5"),
    ("Easily annoyed by people who act unintelligent or uninformed.", "E5"),
    ("I prefer to observe a situation thoroughly before deciding to participate.", "E5"),
    ("I tend to detach emotionally when I feel overwhelmed or overstimulated.", "E5"),
    ("I value knowledge and often research topics extensively before forming an opinion.", "E5"),
    ("I'm not gullible; you must earn my trust, and I will challenge your loyalty.", "E6"),
    ("Friends and family provide the support I feel is necessary in life.", "E6"),
    ("Fear being criticized or judged as being improper by other people.", "E6"),
    ("Look for danger, unsafe people, or unsafe situations.", "E6"),
    ("When afraid of something, I've done what was necessary to overcome my fear.", "E6"),
    ("When I trust people, I can let down my guard and be more sensitive.", "E6"),
    ("Value the belief that everything is going to be all right yet often lack faith in this belief.", "E6"),
    ("Making decisions on my own may cause me anxiety.", "E6"),
    ("When feeling anxious I can be overly vigilant and controlling.", "E6"),
    ("Try to prepare for every contingency.", "E6"),
    ("People may find it difficult to follow my train of thought.", "E7"),
    ("Like to leave my options open; \"don't hem me in\" describes me well.", "E7"),
    ("Dislike being around pessimistic, negative people.", "E7"),
    ("Become frustrated if there is not enough time to do all the fun things I want to do.", "E7"),
    ("Enjoy trying many things and can do many different things fairly well.", "E7"),
    ("Have difficulty making decisions because \"everything looks good.\"", "E7"),
    ("Tend to be excited and impatient about accomplishing plans.", "E7"),
    ("Find it easy to adapt to different people and situations.", "E7"),
    ("Tend to do things in excess and to always want more.", "E7"),
    ("I tend to reframe negative experiences quickly so I can stay positive and move on.", "E7"),
    ("I get bored easily and constantly look for the next exciting thing to do.", "E7"),
    ("I prefer to focus on possibilities and future plans rather than dwelling on problems.", "E7"),
    ("I find it hard to commit to one path because I fear missing out on other options.", "E7"),
    ("I tend to keep conversations light and avoid going too deep into painful topics.", "E7"),
    ("Tend to be possessive and demanding when stressed.", "E8"),
    ("Dislike people nagging me; this makes me quite stubborn.", "E8"),
    ("I'm uncomfortable expressing emotions other than anger.", "E8"),
    ("Love to be challenged and enjoy a good fight.", "E8"),
    ("Proud about being direct, telling it \"like it is,\" and expressing \"tough love.\"", "E8"),
    ("Tend to be rebellious, controlling, and insensitive when stressed.", "E8"),
    ("Impatient with people who are indirect or indecisive.", "E8"),
    ("Have difficulty admitting I'm wrong.", "E8"),
    ("Find it difficult to forgive and can carry a grudge for a long time.", "E8"),
    ("I naturally take charge in situations where others seem hesitant or weak.", "E8"),
    ("I respect people who stand their ground and speak their mind directly.", "E8"),
    ("I have a strong instinct for sensing when someone is being dishonest or manipulative.", "E8"),
    ("I would rather be feared than be seen as weak or vulnerable.", "E8"),
    ("I believe that showing vulnerability is a risk that can be used against me.", "E8"),
    ("Tend to be insightful, objective, and sensitive when not stressed.", "E9"),
    ("Believe it is important for people to be with other people or to belong to a group or an organization.", "E9"),
    ("Have a strong sense of responsibility and I'm a hard worker.", "E9"),
    ("Prefer being with people to being alone.", "E9"),
    ("Tend to see the glass as \"half empty\" and to look for what needs fixing.", "E9"),
    ("Believe it is important to understand my own and other people's feelings.", "E9"),
    ("In relationships, I seek harmony and peace through a sense of belonging and/or by bonding with the other person.", "E9"),
    ("Try to avoid confrontations.", "E9"),
    ("When feeling relaxed I tend to be friendly and responsive to people.", "E9"),
    ("Tend to be shy and withdrawn, especially at social events.", "E9"),
    ("Can be a \"homebody\" and enjoy the comfort and peace of home.", "E9"),
    ("Attracted to habits and routines, can relax easily and tune out reality through TV, daydreaming, a good book, etc.", "E9"),
    ("Sensitive to criticism but try to hide that sensitivity.", "E9"),
    ("Tend to be rational, reasonable, and accepting when not stressed.", "E9"),
    ("Tend to be reflective and to search for the meaning of my life.", "E9"),
    ("Tend to take things too seriously and overreact to small issues.", "E9"),
    ("Tend to socialize with people who are interested in the same things I am.", "E9"),
    ("Dislike confrontation and try to keep the peace.", "E9"),
    ("Tend to be more emotional than most people I know.", "E9"),
    ("Tend to go along with what people say just to get them off my back.", "E9"),
    ("Tend to be distant, stubborn, and pessimistic when stressed.", "E9"),
]


def seed_enneagram_questions():
    db = SessionLocal()

    # Clear existing enneagram questions
    enn_ids = db.query(models.Question.id).filter(models.Question.category == "enneagram")
    db.query(models.Response).filter(
        models.Response.question_id.in_(enn_ids)
    ).delete(synchronize_session=False)
    deleted = db.query(models.Question).filter(
        models.Question.category == "enneagram"
    ).delete(synchronize_session=False)
    if deleted > 0:
        print(f"Cleared {deleted} existing Enneagram questions.")

    print(f"Seeding {len(QUESTIONS)} Enneagram questions with 5-point Likert scale...")

    for text, subtest in QUESTIONS:
        q = models.Question(
            category="enneagram",
            subtest=subtest,
            text=text,
            option_a="Strongly Disagree",
            option_b="Disagree",
            option_c="Neutral",
            option_d="Agree",
            option_e="Strongly Agree",
            option_f=None,
            option_g=None,
            keyed="+",           # Assuming all are positively keyed for now
            correct_answer=None,
        )
        db.add(q)

    db.commit()
    print("Enneagram seeding complete.")
    db.close()


if __name__ == "__main__":
    seed_enneagram_questions()
