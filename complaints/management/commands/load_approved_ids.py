from django.core.management.base import BaseCommand
from complaints.models import ApprovedID


class Command(BaseCommand):
    help = "Load approved student and staff College IDs"

    def handle(self, *args, **options):

        approved_ids = [

            # =====================================================
            # CSE STUDENTS - 30
            # =====================================================

            ("23JUCS167", "CSE", "student"),
            ("25JUCS141", "CSE", "student"),
            ("24JUCS193", "CSE", "student"),
            ("23JUCS218", "CSE", "student"),
            ("25JUCS150", "CSE", "student"),
            ("24JUCS151", "CSE", "student"),
            ("25JUCS209", "CSE", "student"),
            ("23JUCS184", "CSE", "student"),
            ("24JUCS227", "CSE", "student"),
            ("25JUCS155", "CSE", "student"),
            ("23JUCS143", "CSE", "student"),
            ("24JUCS172", "CSE", "student"),
            ("25JUCS231", "CSE", "student"),
            ("23JUCS201", "CSE", "student"),
            ("24JUCS146", "CSE", "student"),
            ("25JUCS188", "CSE", "student"),
            ("23JUCS159", "CSE", "student"),
            ("24JUCS214", "CSE", "student"),
            ("25JUCS163", "CSE", "student"),
            ("23JUCS225", "CSE", "student"),
            ("24JUCS181", "CSE", "student"),
            ("25JUCS147", "CSE", "student"),
            ("23JUCS196", "CSE", "student"),
            ("24JUCS205", "CSE", "student"),
            ("25JUCS220", "CSE", "student"),
            ("23JUCS152", "CSE", "student"),
            ("24JUCS237", "CSE", "student"),
            ("25JUCS174", "CSE", "student"),
            ("23JUCS211", "CSE", "student"),
            ("24JUCS166", "CSE", "student"),

            # =====================================================
            # MBA STUDENTS - 30
            # =====================================================

            ("24JUMBA146", "MBA", "student"),
            ("25JUMBA183", "MBA", "student"),
            ("23JUMBA217", "MBA", "student"),
            ("24JUMBA159", "MBA", "student"),
            ("25JUMBA204", "MBA", "student"),
            ("23JUMBA148", "MBA", "student"),
            ("24JUMBA191", "MBA", "student"),
            ("25JUMBA226", "MBA", "student"),
            ("23JUMBA173", "MBA", "student"),
            ("24JUMBA215", "MBA", "student"),
            ("25JUMBA157", "MBA", "student"),
            ("23JUMBA202", "MBA", "student"),
            ("24JUMBA168", "MBA", "student"),
            ("25JUMBA239", "MBA", "student"),
            ("23JUMBA154", "MBA", "student"),
            ("24JUMBA183", "MBA", "student"),
            ("25JUMBA198", "MBA", "student"),
            ("23JUMBA221", "MBA", "student"),
            ("24JUMBA147", "MBA", "student"),
            ("25JUMBA172", "MBA", "student"),
            ("23JUMBA189", "MBA", "student"),
            ("24JUMBA207", "MBA", "student"),
            ("25JUMBA214", "MBA", "student"),
            ("23JUMBA163", "MBA", "student"),
            ("24JUMBA229", "MBA", "student"),
            ("25JUMBA145", "MBA", "student"),
            ("23JUMBA176", "MBA", "student"),
            ("24JUMBA194", "MBA", "student"),
            ("25JUMBA231", "MBA", "student"),
            ("23JUMBA209", "MBA", "student"),

            # =====================================================
            # AIDS STUDENTS - 30
            # =====================================================

            ("23JUAIDS154", "AIDS", "student"),
            ("24JUAIDS187", "AIDS", "student"),
            ("25JUAIDS142", "AIDS", "student"),
            ("23JUAIDS219", "AIDS", "student"),
            ("24JUAIDS163", "AIDS", "student"),
            ("25JUAIDS198", "AIDS", "student"),
            ("23JUAIDS176", "AIDS", "student"),
            ("24JUAIDS225", "AIDS", "student"),
            ("25JUAIDS157", "AIDS", "student"),
            ("23JUAIDS145", "AIDS", "student"),
            ("24JUAIDS194", "AIDS", "student"),
            ("25JUAIDS211", "AIDS", "student"),
            ("23JUAIDS183", "AIDS", "student"),
            ("24JUAIDS151", "AIDS", "student"),
            ("25JUAIDS229", "AIDS", "student"),
            ("23JUAIDS207", "AIDS", "student"),
            ("24JUAIDS172", "AIDS", "student"),
            ("25JUAIDS166", "AIDS", "student"),
            ("23JUAIDS198", "AIDS", "student"),
            ("24JUAIDS216", "AIDS", "student"),
            ("25JUAIDS185", "AIDS", "student"),
            ("23JUAIDS161", "AIDS", "student"),
            ("24JUAIDS203", "AIDS", "student"),
            ("25JUAIDS149", "AIDS", "student"),
            ("23JUAIDS224", "AIDS", "student"),
            ("24JUAIDS158", "AIDS", "student"),
            ("25JUAIDS217", "AIDS", "student"),
            ("23JUAIDS190", "AIDS", "student"),
            ("24JUAIDS179", "AIDS", "student"),
            ("25JUAIDS234", "AIDS", "student"),

            # =====================================================
            # AIML STUDENTS - 30
            # =====================================================

            ("25JUAIML149", "AIML", "student"),
            ("23JUAIML182", "AIML", "student"),
            ("24JUAIML217", "AIML", "student"),
            ("25JUAIML163", "AIML", "student"),
            ("23JUAIML145", "AIML", "student"),
            ("24JUAIML191", "AIML", "student"),
            ("25JUAIML208", "AIML", "student"),
            ("23JUAIML224", "AIML", "student"),
            ("24JUAIML156", "AIML", "student"),
            ("25JUAIML177", "AIML", "student"),
            ("23JUAIML169", "AIML", "student"),
            ("24JUAIML203", "AIML", "student"),
            ("25JUAIML235", "AIML", "student"),
            ("23JUAIML151", "AIML", "student"),
            ("24JUAIML174", "AIML", "student"),
            ("25JUAIML194", "AIML", "student"),
            ("23JUAIML213", "AIML", "student"),
            ("24JUAIML148", "AIML", "student"),
            ("25JUAIML221", "AIML", "student"),
            ("23JUAIML188", "AIML", "student"),
            ("24JUAIML229", "AIML", "student"),
            ("25JUAIML157", "AIML", "student"),
            ("23JUAIML196", "AIML", "student"),
            ("24JUAIML183", "AIML", "student"),
            ("25JUAIML211", "AIML", "student"),
            ("23JUAIML158", "AIML", "student"),
            ("24JUAIML205", "AIML", "student"),
            ("25JUAIML232", "AIML", "student"),
            ("23JUAIML171", "AIML", "student"),
            ("24JUAIML166", "AIML", "student"),

            # =====================================================
            # ECE STUDENTS - 30
            # =====================================================

            ("24JUEC141", "ECE", "student"),
            ("23JUEC178", "ECE", "student"),
            ("25JUEC163", "ECE", "student"),
            ("24JUEC209", "ECE", "student"),
            ("23JUEC152", "ECE", "student"),
            ("25JUEC187", "ECE", "student"),
            ("24JUEC174", "ECE", "student"),
            ("23JUEC221", "ECE", "student"),
            ("25JUEC145", "ECE", "student"),
            ("24JUEC196", "ECE", "student"),
            ("23JUEC165", "ECE", "student"),
            ("25JUEC214", "ECE", "student"),
            ("24JUEC153", "ECE", "student"),
            ("23JUEC189", "ECE", "student"),
            ("25JUEC201", "ECE", "student"),
            ("24JUEC228", "ECE", "student"),
            ("23JUEC147", "ECE", "student"),
            ("25JUEC172", "ECE", "student"),
            ("24JUEC185", "ECE", "student"),
            ("23JUEC216", "ECE", "student"),
            ("25JUEC233", "ECE", "student"),
            ("24JUEC160", "ECE", "student"),
            ("23JUEC198", "ECE", "student"),
            ("25JUEC154", "ECE", "student"),
            ("24JUEC217", "ECE", "student"),
            ("23JUEC143", "ECE", "student"),
            ("25JUEC226", "ECE", "student"),
            ("24JUEC191", "ECE", "student"),
            ("23JUEC207", "ECE", "student"),
            ("25JUEC179", "ECE", "student"),

            # =====================================================
            # STAFF - 15
            # =====================================================

            ("JU-6841-CSE", "CSE", "staff"),
            ("JU-7196-AIML", "AIML", "staff"),
            ("JU-6538-ECE", "ECE", "staff"),
            ("JU-8274-MBA", "MBA", "staff"),
            ("JU-6915-AIDS", "AIDS", "staff"),
            ("JU-7432-CSE", "CSE", "staff"),
            ("JU-8057-ECE", "ECE", "staff"),
            ("JU-6723-AIML", "AIML", "staff"),
            ("JU-9184-AIDS", "AIDS", "staff"),
            ("JU-7561-MBA", "MBA", "staff"),
            ("JU-6349-ECE", "ECE", "staff"),
            ("JU-7892-CSE", "CSE", "staff"),
            ("JU-8463-MBA", "MBA", "staff"),
            ("JU-7058-AIDS", "AIDS", "staff"),
            ("JU-9631-AIML", "AIML", "staff"),
        ]

        created_count = 0
        existing_count = 0

        for college_id, department, role in approved_ids:

            obj, created = ApprovedID.objects.get_or_create(
                college_id=college_id,
                defaults={
                    "department": department,
                    "role": role,
                    "is_used": False,
                }
            )

            if created:
                created_count += 1
            else:
                existing_count += 1

        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully processed {len(approved_ids)} approved IDs."
            )
        )
        self.stdout.write(
            self.style.SUCCESS(
                f"New IDs added: {created_count}"
            )
        )
        self.stdout.write(
            self.style.WARNING(
                f"Already existing: {existing_count}"
            )
        )
        self.stdout.write("")