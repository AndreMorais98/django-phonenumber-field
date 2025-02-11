from django.core.exceptions import ImproperlyConfigured
from django.test import SimpleTestCase, override_settings
from django.utils import translation

from phonenumber_field import widgets
from phonenumber_field.phonenumber import PhoneNumber
from phonenumber_field.widgets import (
    PhoneNumberInternationalFallbackWidget,
    PhoneNumberPrefixWidget,
)


class PhonePrefixSelectTest(SimpleTestCase):
    def setUp(self):
        super().setUp()
        self.babel_module = widgets.babel

    def test_without_babel(self):
        widgets.babel = None
        with self.assertRaises(ImproperlyConfigured):
            widgets.PhonePrefixSelect()

    def tearDown(self):
        widgets.babel = self.babel_module
        super().tearDown()


class PhoneNumberPrefixWidgetTest(SimpleTestCase):
    def test_initial(self):
        rendered = PhoneNumberPrefixWidget(initial="CN").render("", "")
        self.assertIn('<option value="">---------</option>', rendered)
        self.assertIn('<option value="+86" selected>China +86</option>', rendered)

    @override_settings(PHONENUMBER_DEFAULT_REGION="CN")
    def test_uses_default_region_as_initial(self):
        rendered = PhoneNumberPrefixWidget().render("", "")
        self.assertIn('<option value="">---------</option>', rendered)
        self.assertIn('<option value="+86" selected>China +86</option>', rendered)

    def test_no_initial(self):
        rendered = PhoneNumberPrefixWidget().render("", "")
        self.assertIn('<option value="" selected>---------</option>', rendered)
        self.assertIn('<option value="+86">China +86</option>', rendered)

    @override_settings(USE_I18N=True)
    def test_after_translation_deactivate_all(self):
        translation.deactivate_all()
        rendered = PhoneNumberPrefixWidget().render("", "")
        self.assertIn(
            '<select name="_0"><option value="" selected>---------</option>', rendered
        )

    def test_maxlength_not_in_select(self):
        # Regression test for #490
        widget = PhoneNumberPrefixWidget()
        html = widget.render(name="widget", value=None, attrs={"maxlength": 32})
        self.assertIn('<select name="widget_0">', html)


class PhoneNumberInternationalFallbackWidgetTest(SimpleTestCase):
    def test_fallback_widget_switches_between_national_and_international(self):
        region = "GB"
        number_string = "01606 751 78"
        number = PhoneNumber.from_string(number_string, region=region)
        gb_widget = PhoneNumberInternationalFallbackWidget(region="GB")
        de_widget = PhoneNumberInternationalFallbackWidget(region="DE")
        self.assertHTMLEqual(
            gb_widget.render("number", number),
            '<input name="number" type="text" value="01606 75178" />',
        )
        self.assertHTMLEqual(
            de_widget.render("number", number),
            '<input name="number" type="text" value="+44 1606 75178" />',
        )

        # If there's been a validation error, the value should be included verbatim
        self.assertHTMLEqual(
            gb_widget.render("number", "error"),
            '<input name="number" type="text" value="error" />',
        )
