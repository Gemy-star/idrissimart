"""
Management command to initialize chatbot knowledge base
"""
from django.core.management.base import BaseCommand
from django.utils.translation import gettext as _
from main.chatbot_service import initialize_knowledge_base


class Command(BaseCommand):
    help = 'Initialize chatbot knowledge base with Idrissimart content'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Reset existing knowledge base before initialization',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🤖 Initializing Idrissimart Chatbot...\n')
        )
        
        if options['reset']:
            self.stdout.write('🗑️  Resetting existing knowledge base...')
            from main.chatbot_models import ChatbotKnowledgeBase, ChatbotQuickAction
            ChatbotKnowledgeBase.objects.all().delete()
            ChatbotQuickAction.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('✅ Knowledge base reset completed'))
        
        try:
            # Initialize knowledge base
            initialize_knowledge_base()
            
            # Count created items
            from main.chatbot_models import ChatbotKnowledgeBase, ChatbotQuickAction
            knowledge_count = ChatbotKnowledgeBase.objects.count()
            actions_count = ChatbotQuickAction.objects.count()
            
            self.stdout.write(
                self.style.SUCCESS(f'✅ Created {knowledge_count} knowledge base entries')
            )
            self.stdout.write(
                self.style.SUCCESS(f'✅ Created {actions_count} quick actions')
            )
            
            self.stdout.write(
                self.style.SUCCESS('\n🎉 Chatbot initialization completed successfully!')
            )
            self.stdout.write(
                self.style.WARNING('\n📝 Next steps:')
            )
            self.stdout.write('   1. Run migrations: python manage.py migrate')
            self.stdout.write('   2. Visit /chatbot/ to test the chatbot')
            self.stdout.write('   3. Check the floating widget on any page')
            self.stdout.write('   4. Access admin at /chatbot/admin/ for management')
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error initializing chatbot: {str(e)}')
            )
            raise
