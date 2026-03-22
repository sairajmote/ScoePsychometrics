"""
seed_enneagram.py
Seeds 98 Enneagram personality questions.
Format: Yes / Maybe / No  (options A / B / C)
No grading applied yet — questions are stored without scoring keys.

Run from the project root with the virtual environment active:
    (.venv) PS Z:\\projects\\Psycho\\psycho_one> python backend/seed_enneagram.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import SessionLocal
from backend import models


QUESTIONS_TEXT = [
    "Tend to be possessive and demanding when stressed.",                                                                                     # 1
    "Creative and have an artistic view of life.",                                                                                            # 2
    "Tend to be insightful, objective, and sensitive when not stressed.",                                                                     # 3
    "Tend to be more logical than emotional.",                                                                                                # 4
    "I'm not gullible; you must earn my trust, and I will challenge your loyalty.",                                                          # 5
    "I'm extremely protective of my loved ones and feel good about helping the underdog.",                                                   # 6
    "Work hard and know how to get things done.",                                                                                             # 7
    "Enjoy having control of my own time and private space.",                                                                                 # 8
    "Believe it is important for people to be with other people or to belong to a group or an organization.",                                # 9
    "Critical of myself (my own worst critic) and find it easy to be judgmental and critical of other people as well.",                     # 10
    "Have a strong sense of responsibility and I'm a hard worker.",                                                                          # 11
    "Friends and family provide the support I feel is necessary in life.",                                                                    # 12
    "Believe that rules, regulations, policies, and procedures have a purpose and should be followed and I'm frustrated when others break rules.", # 13
    "Thrive in environments where I can express my creativity.",                                                                              # 14
    "To impress, I may take on too much and make promises I can't keep.",                                                                    # 15
    "Dislike people nagging me; this makes me quite stubborn.",                                                                              # 16
    "People may find it difficult to follow my train of thought.",                                                                           # 17
    "Listen patiently and can be very understanding and comforting to friends.",                                                              # 18
    "Value being well organized and punctual in myself and others.",                                                                         # 19
    "Enjoy the sense of independence that comes from living frugally.",                                                                      # 20
    "Can be deeply hurt by the slightest criticism.",                                                                                        # 21
    "Value exceeding standards and rising to the top of my profession.",                                                                     # 22
    "Have a strong need to be noticed, liked, and appreciated for what I do for others.",                                                   # 23
    "Tend to be romantic and long for the great love of my life to come along.",                                                            # 24
    "Feel different from others, as if \"on the outside looking in.\"",                                                                     # 25
    "Prefer being with people to being alone.",                                                                                              # 26
    "I'm uncomfortable expressing emotions other than anger.",                                                                               # 27
    "Love to be challenged and enjoy a good fight.",                                                                                         # 28
    "Fear being criticized or judged as being improper by other people.",                                                                    # 29
    "Proud about being direct, telling it \"like it is,\" and expressing \"tough love.\"",                                                  # 30
    "Look for danger, unsafe people, or unsafe situations.",                                                                                 # 31
    "Tend to see the glass as \"half empty\" and to look for what needs fixing.",                                                           # 32
    "Prefer people not to know how I feel or what I think unless I tell them.",                                                             # 33
    "Value looking good, presenting a good first impression, and \"dressing for success.\"",                                                # 34
    "Like to leave my options open; \"don't hem me in\" describes me well.",                                                                # 35
    "When afraid of something, I've done what was necessary to overcome my fear.",                                                          # 36
    "Believe it is important to understand my own and other people's feelings.",                                                            # 37
    "Strive to be unique and have done things to avoid being ordinary.",                                                                    # 38
    "Dislike being around pessimistic, negative people.",                                                                                    # 39
    "When I trust people, I can let down my guard and be more sensitive.",                                                                  # 40
    "In relationships, I seek harmony and peace through a sense of belonging and/or by bonding with the other person.",                     # 41
    "Tend to be rebellious, controlling, and insensitive when stressed.",                                                                   # 42
    "Can be caught in a fantasy world of romance and imagination.",                                                                          # 43
    "May hesitate while I try to organize my thoughts and may not speak at all if I'm not comfortable with what I want to say.",            # 44
    "Can be critical, cynical, and argumentative and can act intellectually superior.",                                                     # 45
    "Value the belief that everything is going to be all right yet often lack faith in this belief.",                                       # 46
    "Motivated by the need to be correct, fair, and self-disciplined.",                                                                     # 47
    "Become frustrated if there is not enough time to do all the fun things I want to do.",                                                 # 48
    "Have a strong sense of right and wrong and strive for perfection.",                                                                    # 49
    "Enjoy trying many things and can do many different things fairly well.",                                                               # 50
    "Tend to experience more melancholy than most people I know.",                                                                          # 51
    "Try to avoid confrontations.",                                                                                                          # 52
    "Have difficulty making decisions because \"everything looks good.\"",                                                                  # 53
    "Like people to depend on me and deliver on my promises.",                                                                              # 54
    "When feeling relaxed I tend to be friendly and responsive to people.",                                                                 # 55
    "Tend to be excited and impatient about accomplishing plans.",                                                                          # 56
    "Tend to be shy and withdrawn, especially at social events.",                                                                           # 57
    "Can be a \"homebody\" and enjoy the comfort and peace of home.",                                                                       # 58
    "Impatient with people who are indirect or indecisive.",                                                                                # 59
    "Easily discern what is wrong in a situation and how it could be done better.",                                                        # 60
    "Have ideas, theories, and opinions about almost everything.",                                                                          # 61
    "Have been told I am not in touch with my emotions.",                                                                                   # 62
    "Making decisions on my own may cause me anxiety.",                                                                                     # 63
    "I feel uncomfortable around loud, emotional people.",                                                                                  # 64
    "Attracted to habits and routines, can relax easily and tune out reality through TV, daydreaming, a good book, etc.",                  # 65
    "Sensitive to criticism but try to hide that sensitivity.",                                                                             # 66
    "Attracted to what is intense and out of the ordinary.",                                                                                # 67
    "Tend to be rational, reasonable, and accepting when not stressed.",                                                                    # 68
    "Tend to be reflective and to search for the meaning of my life.",                                                                     # 69
    "Believe that my motives for helping others are noble and helpful.",                                                                    # 70
    "Do not consider being a perfectionist a negative thing and like to make sure all the details are just right.",                        # 71
    "I'm told I'm a \"nice person\" and dislike putting myself first.",                                                                    # 72
    "Believe that negative feelings are an obstacle to getting the job done.",                                                              # 73
    "Find it easy to adapt to different people and situations.",                                                                            # 74
    "Personal integrity is extremely important to me.",                                                                                     # 75
    "Tend to be idealistic and ambitious and want to contribute something positive to the world.",                                          # 76
    "Tend to take things too seriously and overreact to small issues.",                                                                     # 77
    "Enjoy spending time alone pursuing my personal interests.",                                                                            # 78
    "Have difficulty admitting I'm wrong.",                                                                                                 # 79
    "Find it difficult to forgive and can carry a grudge for a long time.",                                                                # 80
    "Manners and good taste are extremely important to me.",                                                                                # 81
    "Tend to do things in excess and to always want more.",                                                                                 # 82
    "Motivated by the need to be appreciated, loved, and connected to people.",                                                             # 83
    "Feel that something is missing in my life.",                                                                                           # 84
    "When feeling anxious I can be overly vigilant and controlling.",                                                                       # 85
    "Tend to socialize with people who are interested in the same things I am.",                                                            # 86
    "Feel envious of other people's relationships, lifestyles, and accomplishments.",                                                       # 87
    "Easily annoyed by people who act unintelligent or uninformed.",                                                                        # 88
    "Enjoy having elegant, refined, unique things that no one else has.",                                                                   # 89
    "Dislike confrontation and try to keep the peace.",                                                                                     # 90
    "Love to work and be productive, and work has tended to be a top priority in my life.",                                                # 91
    "Try to prepare for every contingency.",                                                                                                # 92
    "Tend to be more emotional than most people I know.",                                                                                   # 93
    "Have been goal-oriented for as long as I can remember.",                                                                              # 94
    "Need to feel close to people and feel rejected and hurt if I don't experience that closeness.",                                       # 95
    "Tend to go along with what people say just to get them off my back.",                                                                  # 96
    "Routine and structure help me stay focused and accomplish things.",                                                                    # 97
    "Tend to be distant, stubborn, and pessimistic when stressed.",                                                                        # 98
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

    print(f"Seeding {len(QUESTIONS_TEXT)} Enneagram questions...")

    for text in QUESTIONS_TEXT:
        q = models.Question(
            category="enneagram",
            subtest=None,        # No grading yet
            text=text,
            option_a="Yes",
            option_b="Maybe",
            option_c="No",
            option_d="",         # NOT NULL column — use empty string
            option_e=None,
            keyed=None,
            correct_answer=None,
        )
        db.add(q)

    db.commit()
    print("Enneagram seeding complete.")
    db.close()


if __name__ == "__main__":
    seed_enneagram_questions()
