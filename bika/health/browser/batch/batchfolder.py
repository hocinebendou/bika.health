from Products.CMFCore.utils import getToolByName
from bika.health import bikaMessageFactory as _
from bika.lims.browser.batchfolder import BatchFolderContentsView as BaseView


class BatchFolderContentsView(BaseView):

    def __init__(self, context, request):
        super(BatchFolderContentsView, self).__init__(context, request)
        self.title = _("Cases")
        self.columns = {
            'BatchID': {'title': _('Case ID')},
            'Doctor': {'title': _('Doctor'),
                       'index': 'getDoctorTitle'},
            'Client': {'title': _('Client'),
                       'index': 'getClientTitle'},
            'OnsetDate': {'title': _('Onset Date')},
            'state_title': {'title': _('State'), 'sortable': False},
         }
        self.review_states = [  # leave these titles and ids alone
            {'id':'default',
             'contentFilter': {'cancellation_state':'active',
                               'review_state': ['open', 'sample_received', 'to_be_verified', 'verified'],
                               'sort_on':'created',
                               'sort_order': 'reverse'},
             'title': _('Open'),
             'columns':['BatchID',
                        'Doctor',
                        'Client',
                        'OnsetDate',
                        'state_title', ]
             },
            {'id':'closed',
             'contentFilter': {'review_state': 'closed',
                               'sort_on':'created',
                               'sort_order': 'reverse'},
             'title': _('Closed'),
             'columns':['BatchID',
                        'Doctor',
                        'Client',
                        'OnsetDate',
                        'state_title', ]
             },
            {'id':'cancelled',
             'title': _('Cancelled'),
             'contentFilter': {'cancellation_state': 'cancelled',
                               'sort_on':'created',
                               'sort_order': 'reverse'},
             'columns':['BatchID',
                        'Doctor',
                        'Client',
                        'OnsetDate',
                        'state_title', ]
             },
            {'id':'all',
             'title': _('All'),
             'contentFilter':{'sort_on':'created',
                              'sort_order': 'reverse'},
             'columns':['BatchID',
                        'Doctor',
                        'Client',
                        'OnsetDate',
                        'state_title', ]
             },
        ]

    def folderitems(self):
        self.filter_indexes = None

        items = BaseView.folderitems(self)
        pm = getToolByName(self.context, "portal_membership")
        member = pm.getAuthenticatedMember()
        roles = member.getRoles()
        showpatientinfo = 'Manager' in roles or 'LabManager' in roles \
                        or 'LabClerk' in roles
        if showpatientinfo:
            # Add Client Patient fields
            self.columns['Patient'] = {'title': _("Patient")}
            self.columns['getClientPatientID'] = {'title': _("Client PID")}
            for rs in self.review_states:
                i = rs['columns'].index('BatchID') + 1
                rs['columns'].insert(i, 'getClientPatientID')
                rs['columns'].insert(i, 'Patient')

        for x in range(len(items)):
            if 'obj' not in items[x]:
                continue
            obj = items[x]['obj']

            bid = obj.getBatchID()
            items[x]['BatchID'] = bid

            client = obj.Schema()['Client'].get(obj)
            doctor = obj.Schema()['Doctor'].get(obj)

            items[x]['replace']['Doctor'] = doctor \
                and "<a href='%s'>%s</a>" % \
                (doctor.absolute_url(),
                 doctor.Title()) or ''

            items[x]['replace']['Client'] = client \
                and "<a href='%s'>%s</a>" % \
                (client.absolute_url(),
                 client.Title()) or ''

            OnsetDate = obj.Schema()['OnsetDate'].get(obj)
            items[x]['replace']['OnsetDate'] = OnsetDate \
                and self.ulocalized_time(OnsetDate) or ''

            if showpatientinfo:
                patient = obj.Schema()['Patient'].get(obj)
                items[x]['Patient'] = patient and patient or ''
                items[x]['replace']['Patient'] = patient \
                                and "<a href='%s'>%s</a>" % \
                                (patient.absolute_url(),
                                 patient.Title()) or ''
                items[x]['getClientPatientID'] = patient \
                                and patient.getClientPatientID() \
                                or ''
                items[x]['replace']['getClientPatientID'] = patient \
                                and "<a href='%s'>%s</a>" % \
                                    (patient.absolute_url(), 
                                     items[x]['getClientPatientID']) \
                                or ''
        return items
