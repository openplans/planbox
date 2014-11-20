import requests
from django.conf import settings
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext as _
from planbox_data.models import clone_pre_save, Section, CloneableModelMixin


@python_2_unicode_compatible
class Preauthorization (CloneableModelMixin, models.Model):
    username = models.TextField(blank=True, help_text=_('The username of the Shareabouts user'))
    project = models.OneToOneField('planbox_data.Project', related_name='shareabouts_preauthorization')

    def __str__(self):
        return self.username


def clone_section_dataset(sender, orig_inst, new_inst, *args, **kwargs):
    if orig_inst.type == 'shareabouts' and 'dataset_url' in orig_inst.details:
        username = settings.SHAREABOUTS_USERNAME
        password = settings.SHAREABOUTS_PASSWORD

        # Get the dataset list URL
        orig_dataset_url = orig_inst.details['dataset_url']
        last_slash = orig_dataset_url.rfind('/')
        dataset_list_url = orig_dataset_url[:last_slash]

        # Send a request to clone the dataset
        response = requests.post(dataset_list_url,
            headers={'X-Shareabouts-Clone': orig_dataset_url},
            auth=(username, password))

        # Use the new dataset URL in the cloned section
        if response.status_code in (201, 202):
            new_inst.details['dataset_url'] = response.json()['url']
        else:
            raise Exception('Invalid response from %s: (%s) %s' % (dataset_list_url, response.status_code, response.text))
clone_pre_save.connect(clone_section_dataset, sender=Section, dispatch_uid="shareabouts-section-clone-dataset-signal")
