from flask import Flask, render_template, request, session, redirect, url_for

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

#TODO: Add variant don't know
class WeaponRecommender:
    def __init__(self):
        self.weapon_db = {
            'ПП': {
                'name': 'Пистолеты-пулеметы',
                'weapons': ['PP-19-01 "Витязь"', 'MP5', 'MPX', 'Kedr-B', 'PP-91 "Кедр"'],
                'calibers': ['9x19mm', '9x18mm'],
                'budget': 'low',
                'range': 'close',
                'pros': ['Стреляет очень быстро', 'Легко управлять', 'Дешевые патроны'],
                'cons': ['Слабо бьет на расстоянии', 'Требует много патронов для убийства']
            },
            'АК_5.45': {
                'name': 'Универсальные автоматы (5.45x39)',
                'weapons': ['АК-74Н', 'АК-74М', 'АК-105', 'АКС-74У'],
                'calibers': ['5.45x39mm'],
                'budget': 'medium',
                'range': 'medium',
                'pros': ['Подходит для любой дистанции', 'Надежный', 'Патроны легко найти'],
                'cons': ['Нужно учиться контролировать отдачу']
            },
            'АК_7.62': {
                'name': 'Мощные автоматы (7.62x39)',
                'weapons': ['АКМ', 'АК-103', 'ОП-СКС'],
                'calibers': ['7.62x39mm'],
                'budget': 'low',
                'range': 'medium',
                'pros': ['Сильно бьет', 'Меньше выстрелов для убийства', 'Прощает ошибки'],
                'cons': ['Сильная отдача', 'Тяжелый']
            },
            'АК_5.56': {
                'name': 'Современные автоматы (5.56x45)',
                'weapons': ['АДAR 2-15', 'M4A1', 'HK 416A5'],
                'calibers': ['5.56x45mm'],
                'budget': 'high',
                'range': 'medium',
                'pros': ['Точный', 'Низкая отдача', 'Хорошая пробиваемость'],
                'cons': ['Дорогие патроны', 'Сложно найти']
            },
            'ДМР': {
                'name': 'Точные винтовки',
                'weapons': ['ОП-СКС', 'Vepr KM/VPO-136', 'RFB', 'SR-25'],
                'calibers': ['7.62x39mm', '7.62x51mm', '.308 Win'],
                'budget': 'medium',
                'range': 'long',
                'pros': ['Убивает с 1-2 выстрелов', 'Точный на расстоянии'],
                'cons': ['Сложно в ближнем бою', 'Медленно стреляет']
            },
            'Снайперские': {
                'name': 'Снайперские винтовки',
                'weapons': ['Мосина', 'SV-98', 'DVL-10', 'M700'],
                'calibers': ['7.62x54mmR', '.308 Win', '.338 Lapua'],
                'budget': 'high',
                'range': 'long',
                'pros': ['Убивает с одного выстрела', 'Безопасная дистанция'],
                'cons': ['Бесполезен вблизи', 'Очень медленный']
            },
            'Дробовики': {
                'name': 'Дробовики',
                'weapons': ['MP-133', 'MP-153', 'Saiga-12k'],
                'calibers': ['12x70', '20x70'],
                'budget': 'low',
                'range': 'close',
                'pros': ['Очень сильный вблизи', 'Не требует точного прицеливания'],
                'cons': ['Бесполезен на расстоянии', 'Медленная перезарядка']
            }
        }

        # Данные о картах
        self.maps_data = {
            'Custom': {'distance': 'B', 'image': 'custom.png'},
            'Factory': {'distance': 'A', 'image': 'factory.png'},
            'Ground Zero': {'distance': 'B', 'image': 'ground_zero.png'},
            'Interchange': {'distance': 'A', 'image': 'interchange.png'},
            'Lighthouse': {'distance': 'C', 'image': 'lighthouse.png'},
            'Reserve': {'distance': 'B', 'image': 'reserve.png'},
            'Shoreline': {'distance': 'B', 'image': 'shoreline.png'},
            'Streets of Tarkov': {'distance': 'B', 'image': 'streets.png'},
            'The Lab': {'distance': 'A', 'image': 'lab.png'},
            'Woods': {'distance': 'C', 'image': 'woods.png'}
        }

    def calculate_recommendation(self, answers):
        scores = {category: 0 for category in self.weapon_db.keys()}

        # Определяем дистанцию по выбранной карте
        if 'q2' in answers:
            selected_map = answers['q2']
            if selected_map in self.maps_data:
                distance = self.maps_data[selected_map]['distance']
                if distance == 'A':  # Ближняя
                    scores['ПП'] += 3
                    scores['Дробовики'] += 3
                    scores['АК_5.45'] += 1
                elif distance == 'B':  # Средняя
                    scores['АК_5.45'] += 3
                    scores['АК_7.62'] += 3
                    scores['АК_5.56'] += 2
                else:  # Дальняя
                    scores['Снайперские'] += 3
                    scores['ДМР'] += 2
                    scores['АК_5.56'] += 1

        # Стиль игры
        if answers.get('q1') == 'A':  # Агрессивный
            scores['ПП'] += 3
            scores['Дробовики'] += 2
            scores['АК_5.45'] += 1
        elif answers.get('q1') == 'B':  # Осторожный
            scores['Снайперские'] += 3
            scores['ДМР'] += 2
            scores['АК_5.56'] += 1
        else:  # Смешанный
            scores['АК_5.45'] += 2
            scores['АК_7.62'] += 2
            scores['АК_5.56'] += 1

        # Приоритеты в оружии
        if answers.get('q3') == 'A':  # Скорострельность
            scores['ПП'] += 3
            scores['АК_5.45'] += 2
        elif answers.get('q3') == 'B':  # Мощность
            scores['АК_7.62'] += 3
            scores['ДМР'] += 2
            scores['Снайперские'] += 1
        else:  # Контроль отдачи
            scores['АК_5.45'] += 2
            scores['АК_5.56'] += 2
            scores['ПП'] += 1

        # Бюджет
        if answers.get('q4') == 'A':  # Экономный
            scores['ПП'] += 2
            scores['АК_7.62'] += 2
            scores['Дробовики'] += 2
        elif answers.get('q4') == 'B':  # Средний
            scores['АК_5.45'] += 2
            scores['ДМР'] += 1
        else:  # Не важен
            scores['АК_5.56'] += 2
            scores['Снайперские'] += 2

        # Прицелы
        if answers.get('q5') == 'C':  # Оптика с увеличением
            scores['Снайперские'] += 2
            scores['ДМР'] += 1
        elif answers.get('q5') == 'B':  # Простой прицел
            scores['АК_5.45'] += 1
            scores['АК_5.56'] += 1

        # Уточняющие вопросы
        if answers.get('q6') == 'A':  # Много стрелять в ближнем бою
            scores['ПП'] += 2
        elif answers.get('q6') == 'B':  # Мощный выстрел в ближнем бою
            scores['Дробовики'] += 2

        if answers.get('q7') == 'A':  # Баланс силы и скорости
            scores['АК_7.62'] += 2
        elif answers.get('q7') == 'B':  # Максимальная мощь
            scores['ДМР'] += 2
            scores['Снайперские'] += 1

        if answers.get('q8') == 'A':  # Практичность важнее
            scores['АК_7.62'] += 1
            scores['ПП'] += 1
        elif answers.get('q8') == 'B':  # Современность важнее
            scores['АК_5.56'] += 1
            scores['АК_5.45'] += 1

        if answers.get('q9') == 'A':  # Скорость реакции
            scores['ПП'] += 1
            scores['АК_5.45'] += 1
        elif answers.get('q9') == 'B':  # Мощность выстрела
            scores['АК_7.62'] += 1
            scores['Дробовики'] += 1

        if answers.get('q10') == 'A':  # Статичная позиция
            scores['Снайперские'] += 1
            scores['ДМР'] += 1
        elif answers.get('q10') == 'B':  # Подвижность
            scores['АК_5.45'] += 1
            scores['АК_5.56'] += 1

        # Финальные вопросы
        if answers.get('q11') == 'A':  # Короткое и простое
            scores['ПП'] += 1
            scores['Дробовики'] += 1
        elif answers.get('q11') == 'B':  # Длинное и серьезное
            scores['АК_7.62'] += 1
            scores['ДМР'] += 1
        else:  # С прицелом для далекой стрельбы
            scores['Снайперские'] += 1
            scores['АК_5.56'] += 1

        if answers.get('q12') == 'B':  # Уверен в попадании
            scores['Снайперские'] += 1
            scores['ДМР'] += 1
        else:  # Стреляет в корпус
            scores['ПП'] += 1
            scores['Дробовики'] += 1

        if answers.get('q13') == 'A':  # Важна доступность патронов
            scores['АК_5.45'] += 1
            scores['АК_7.62'] += 1
            scores['ПП'] += 1

        if answers.get('q14') == 'A':  # Тихие выстрелы
            scores['ПП'] += 1
            scores['АК_5.45'] += 1

        if answers.get('q15') == 'A':  # Выживание
            scores['ПП'] += 1
            scores['Дробовики'] += 1
        elif answers.get('q15') == 'B':  # Убийства
            scores['АК_7.62'] += 1
            scores['Снайперские'] += 1
        else:  # Контроль
            scores['АК_5.45'] += 1
            scores['АК_5.56'] += 1

        # Находим лучшую категорию
        recommended_category = max(scores, key=scores.get)
        return recommended_category, scores[recommended_category]


# Все вопросы
QUESTIONS = {
    'q1': {
        'question': "1. Какой игровой стиль тебе ближе?",
        'options': {
            'A': 'Агрессивный - уверенный (быстрый выход на контакт, движение в лоб)',
            'B': 'Осторожный - боязливый (занятие позиции, выжидание)',
            'C': 'Смешанный - стратег (стараюсь оценить ситуацию и действовать по обстоятельствам)'
        }
    },
    'q2': {
        'question': "2. На какой карте ты планируешь чаще всего играть?",
        'type': 'maps'
    },
    'q3': {
        'question': "3. Что для тебя важнее в оружии?",
        'options': {
            'A': 'Скорострельность и возможность "залить" противника свинцом',
            'B': 'Мощность и точность: чтобы уложить с одного-двух выстрелов',
            'C': 'Низкая отдача, чтобы было легко контролить автоматический огонь'
        }
    },
    'q4': {
        'question': "4. Насколько для тебя важен бюджет (патроны и стоимость оружия)?",
        'options': {
            'A': 'Очень важен, хочу экономить и не разоряться на каждом выстреле',
            'B': 'Готов платить за эффективность, но в разумных пределах',
            'C': 'Патроны и оружие должны быть максимально эффективными, стоимость второстепенна'
        }
    },
    'q5': {
        'question': "5. Ты планируешь часто использовать прицелы?",
        'options': {
            'A': 'Нет, буду полагаться на мушку',
            'B': 'Да, но что-то простое вроде точки на стекле',
            'C': 'Да, хочу иметь возможность приближения цели в прицеле для точной стрельбы'
        }
    }
}

# Уточняющие вопросы
FOLLOWUP_QUESTIONS = {
    'q6': {
        'question': "6. Что тебе кажется эффективнее в ближнем бою?",
        'options': {
            'A': 'Залить врага пулями (много стрелять)',
            'B': 'Убить с одного сильного выстрела'
        },
        'trigger': {'q': 'q2', 'condition': 'distance_A'}  # Если выбрана карта с ближней дистанцией
    },
    'q7': {
        'question': "7. Ты хочешь оружие, которое:",
        'options': {
            'A': 'Бьет достаточно сильно, но можно стрелять быстро',
            'B': 'Бьет очень сильно, даже если стреляет медленно'
        },
        'trigger': {'q': 'q3', 'answer': 'B'}
    },
    'q8': {
        'question': "8. Насколько ты готов к тому, что твое оружие может быть не самым современным?",
        'options': {
            'A': 'Полностью готов, главное — практичность и цена',
            'B': 'Хочу что-то более современное, даже если чуть дороже'
        },
        'trigger': {'q': 'q4', 'answer': ['A', 'B']}
    },
    'q9': {
        'question': "9. Что важнее в неожиданной встрече с врагом?",
        'options': {
            'A': 'Успеть выстрелить первым',
            'B': 'Убить врага с одного выстрела'
        },
        'trigger': {'q': 'q1', 'answer': ['B', 'C']}
    },
    'q10': {
        'question': "10. При стрельбе издалека ты:",
        'options': {
            'A': 'Сижу на одном месте и жду',
            'B': 'Перебегаю между укрытиями'
        },
        'trigger': {'q': 'q5', 'answer': 'C'}
    }
}

# Финальные вопросы
FINAL_QUESTIONS = {
    'q11': {
        'question': "11. Какое оружие выглядит для тебя надежнее?",
        'options': {
            'A': 'Короткое и простое',
            'B': 'Длинное и серьезное',
            'C': 'С большим прицелом для далекой стрельбы'
        }
    },
    'q12': {
        'question': "12. Насколько ты уверен в своей способности точно попадать в цель?",
        'options': {
            'A': 'Не очень, буду стрелять в корпус',
            'B': 'Уверен, буду стараться целиться в критически важные части'
        }
    },
    'q13': {
        'question': "13. Важно ли для тебя, чтобы оружие и патроны часто встречались у врагов?",
        'options': {
            'A': 'Да, хочу легко пополнять боезапас',
            'B': 'Не очень, готов покупать специальные патроны у торговцев'
        }
    },
    'q14': {
        'question': "14. Как ты относишься к громкости выстрела?",
        'options': {
            'A': 'Лучше тише, чтобы не привлекать лишнего внимания',
            'B': 'Не имеет значения, главное — эффективность'
        }
    },
    'q15': {
        'question': "15. Что для тебя станет показателем успешного выбора оружия?",
        'options': {
            'A': 'Смог добыть лут и выжить',
            'B': 'Смог уверенно убить 1-2 врагов',
            'C': 'Почувствовал контроль над ситуацией и уверенность'
        }
    }
}

# Объединяем все вопросы
ALL_QUESTIONS = {**QUESTIONS, **FOLLOWUP_QUESTIONS, **FINAL_QUESTIONS}

# Общее количество вопросов (всегда 15)
TOTAL_QUESTIONS = 15


@app.route('/')
def index():
    session.clear()
    session['answers'] = {}
    session['current_question'] = 'q1'

    # Создаем фиксированный порядок вопросов (всегда 15 вопросов)
    session['question_order'] = ['q1', 'q2', 'q3', 'q4', 'q5', 'q6', 'q7', 'q8', 'q9', 'q10', 'q11', 'q12', 'q13',
                                 'q14', 'q15']
    session['asked_questions'] = ['q1']  # Вопросы, которые действительно будут заданы

    return redirect(url_for('question'))


@app.route('/question', methods=['GET', 'POST'])
def question():
    if 'answers' not in session:
        return redirect(url_for('index'))

    if request.method == 'POST':
        current_q = session['current_question']
        answer = request.form.get('answer')

        if answer:
            session['answers'][current_q] = answer
            session.modified = True

            # Определяем следующий вопрос
            current_index = session['question_order'].index(current_q)
            next_index = current_index + 1

            # Пропускаем вопросы, которые не нужно задавать
            while next_index < TOTAL_QUESTIONS:
                next_q = session['question_order'][next_index]

                # Проверяем, нужно ли задавать этот вопрос
                should_ask = check_should_ask(next_q, session['answers'])

                if should_ask:
                    session['current_question'] = next_q
                    if next_q not in session['asked_questions']:
                        session['asked_questions'].append(next_q)
                    break
                else:
                    next_index += 1
            else:
                # Если дошли до конца
                return redirect(url_for('result'))

            return redirect(url_for('question'))

    # GET запрос - показываем текущий вопрос
    current_q = session['current_question']
    question_data = ALL_QUESTIONS[current_q]

    # Рассчитываем прогресс (на основе порядка вопросов, а не заданных)
    current_index = session['question_order'].index(current_q)
    progress = (current_index + 1) / TOTAL_QUESTIONS * 100

    # Для вопроса с картами передаем дополнительную информацию
    maps_data = None
    if current_q == 'q2':
        recommender = WeaponRecommender()
        maps_data = recommender.maps_data

    return render_template('question.html',
                           question=question_data,
                           qid=current_q,
                           progress=progress,
                           total_questions=TOTAL_QUESTIONS,
                           current_number=current_index + 1,
                           maps_data=maps_data)


def check_should_ask(question_id, answers):
    """Проверяет, нужно ли задавать вопрос based on предыдущих ответов"""
    if question_id in ['q1', 'q2', 'q3', 'q4', 'q5', 'q11', 'q12', 'q13', 'q14', 'q15']:
        return True

    triggers = {
        'q6': {'q': 'q2', 'condition': 'distance_A'},  # Если выбрана карта с ближней дистанцией
        'q7': {'q': 'q3', 'answer': 'B'},
        'q8': {'q': 'q4', 'answer': ['A', 'B']},
        'q9': {'q': 'q1', 'answer': ['B', 'C']},
        'q10': {'q': 'q5', 'answer': 'C'}
    }

    if question_id in triggers:
        trigger = triggers[question_id]
        prerequisite_q = trigger['q']

        if prerequisite_q not in answers:
            return False

        if 'condition' in trigger:
            if trigger['condition'] == 'distance_A':
                # Проверяем, выбрана ли карта с ближней дистанцией
                recommender = WeaponRecommender()
                selected_map = answers.get('q2')
                if selected_map in recommender.maps_data:
                    return recommender.maps_data[selected_map]['distance'] == 'A'
                return False
        elif 'answer' in trigger:
            expected_answers = trigger['answer'] if isinstance(trigger['answer'], list) else [trigger['answer']]
            return answers[prerequisite_q] in expected_answers

    return True


@app.route('/result')
def result():
    if 'answers' not in session or not session['answers']:
        return redirect(url_for('index'))

    recommender = WeaponRecommender()
    category, score = recommender.calculate_recommendation(session['answers'])
    weapon_info = recommender.weapon_db[category]

    return render_template('result.html',
                           category=category,
                           weapon_info=weapon_info,
                           answers=session['answers'])


@app.route('/restart')
def restart():
    session.clear()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)