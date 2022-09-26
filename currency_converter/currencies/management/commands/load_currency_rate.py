from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError

from currency_converter.currencies.services import CurrencyRateService, CurrencyService


class Command(BaseCommand):
    help = "Loads currency rate for specific period"

    def add_arguments(self, parser):
        period_help = f"Available choices: {', '.join(CurrencyRateService.get_available_periods())}"
        parser.add_argument("symbols", nargs="+", type=str)
        parser.add_argument("--period", type=str, help=period_help)

    def handle(self, *args, **options):
        period = options["period"] if options["period"] else "1d"

        service = CurrencyService()
        currencies = list(
            service.get_or_generate_currencies(
                currencies=options["symbols"]
            ).values_list("symbol", flat=True)
        )
        try:
            created, updated = service.load_currencies(
                currencies=currencies, period=period
            )
            success_message = f"Created {created} and updated {updated} rates"
            self.stdout.write(self.style.SUCCESS(success_message))
            service.clean_currencies()
        except ValidationError as e:
            raise CommandError(f"{e.message}. Rollback changes...")
