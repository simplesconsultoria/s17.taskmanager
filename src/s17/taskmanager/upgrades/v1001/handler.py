# -*- coding: utf-8 -*-

from s17.taskmanager.config import PROJECTNAME

import logging

logger = logging.getLogger(PROJECTNAME)
PROFILE_ID = 'profile-s17.taskmanager:default'


def update_content_type_information(context):
    """Update content type information as rename of Task Panel was incomplete.
    """
    context.runImportStepFromProfile(PROFILE_ID, 'typeinfo')
    logger.info('Portal type information was updated')
