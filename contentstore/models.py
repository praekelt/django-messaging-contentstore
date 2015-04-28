from django.db import models
from django.utils.translation import ugettext_lazy as _


class Schedule(models.Model):

    """
    Schdules (sometimes referred to as Protocols) are the method used to
    define the rate and frequency at which the messages are sent to
    the recipient
    """
    minute = models.CharField(_('minute'), max_length=64, default='*')
    hour = models.CharField(_('hour'), max_length=64, default='*')
    day_of_week = models.CharField(
        _('day of week'), max_length=64, default='*',
    )
    day_of_month = models.CharField(
        _('day of month'), max_length=64, default='*',
    )
    month_of_year = models.CharField(
        _('month of year'), max_length=64, default='*',
    )

    class Meta:
        verbose_name = _('schedule')
        verbose_name_plural = _('schedules')
        ordering = ['month_of_year', 'day_of_month',
                    'day_of_week', 'hour', 'minute']

    def __unicode__(self):
        rfield = lambda f: f and str(f).replace(' ', '') or '*'
        return '{0} {1} {2} {3} {4} (m/h/d/dM/MY)'.format(
            rfield(self.minute), rfield(self.hour), rfield(self.day_of_week),
            rfield(self.day_of_month), rfield(self.month_of_year),
        )
