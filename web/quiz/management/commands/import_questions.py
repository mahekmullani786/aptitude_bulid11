import pandas as pd
from django.core.management.base import BaseCommand, CommandError
from quiz.models import Question
from django.db import transaction
try:
    import requests
except ImportError:
    requests = None
from io import BytesIO


class Command(BaseCommand):
    help = 'Import questions from an Excel file (questions.xlsx). Columns: Question, Option_A, Option_B, Option_C, Option_D, Answer'

    def add_arguments(self, parser):
        parser.add_argument("questions.xlsx", type=str, required=True, help='C:\Users\LOQ\Downloads\aptitudebulid-main>')

    def handle(self, *args, **options):
        source = options['questions.xlsx']
        try:
            if source.startswith('http'):
                resp = requests.get(source)
                resp.raise_for_status()
                data = BytesIO(resp.content)
                df = pd.read_excel(data)
            else:
                df = pd.read_excel(source)
        except Exception as e:
            raise CommandError(f'Failed to read the Excel file: {e}')

        required_cols = {'Question', 'Option_A', 'Option_B', 'Option_C', 'Option_D', 'Answer'}
        if not required_cols.issubset(set(df.columns)):
            raise CommandError(f'Excel file must contain columns: {required_cols}')

        created = 0
        skipped = 0
        with transaction.atomic():
            for _, row in df.iterrows():
                q_text = str(row['Question']).strip()
                if not q_text:
                    skipped += 1
                    continue
                # normalize answer to single letter if possible
                ans = str(row['Answer']).strip()
                if ans.upper() in ['A', 'B', 'C', 'D']:
                    ans_letter = ans.upper()
                else:
                    # try to match by option text
                    opts = {
                        'A': str(row['Option_A']).strip(),
                        'B': str(row['Option_B']).strip(),
                        'C': str(row['Option_C']).strip(),
                        'D': str(row['Option_D']).strip(),
                    }
                    matched = None
                    for k, v in opts.items():
                        if v and v.lower() == ans.lower():
                            matched = k
                            break
                    ans_letter = matched or 'A'

                # avoid duplicates by question text
                obj, created_flag = Question.objects.get_or_create(
                    question_text=q_text,
                    defaults={
                        'option_a': str(row['Option_A']),
                        'option_b': str(row['Option_B']),
                        'option_c': str(row['Option_C']),
                        'option_d': str(row['Option_D']),
                        'answer': ans_letter,
                    }
                )
                if created_flag:
                    created += 1
                else:
                    skipped += 1

        self.stdout.write(self.style.SUCCESS(f'Import finished. Created: {created}, Skipped (duplicates/invalid): {skipped}'))
