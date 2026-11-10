from datetime import datetime, timezone, timedelta
import sys
from pathlib import Path
import pytest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import team_contributions as team
import team_delivery as delivery
from test_grace_gems_daily import packet, reviewed
AT = datetime(2026, 10, 28, 20, tzinfo=timezone.utc)

@pytest.fixture
def participant(tmp_path):
    root = tmp_path / 'private'
    source = tmp_path / 'source-2026-10-28.txt'; source.write_text('Reviewed fictional evidence')
    ref = {'path': str(source), 'sha256': delivery.sha(source.read_bytes())}
    config = {'private_root': str(root), 'owner': 'hannah', 'project': 'grace-gems', 'host': 'test-host',
              'account': 'participant-test', 'folder_id': 'folder', 'drive_id': 'drive',
              'adopted': True, 'adopted_at': '2026-10-27T12:00:00Z', 'adoption_evidence': ref,
              'allowed_sources': {'source-1': str(source)}, 'drive_access': {'verified': True, 'account': 'participant-test',
              'folder_id': 'folder', 'drive_id': 'drive', 'observed_at': AT.isoformat()}}
    p = packet('hannah'); p['sources'][0]['sha256'] = ref['sha256']; reviewed(p)
    completion = {'status': 'completed', 'trigger': 'explicit-project-dream', 'host': 'test-host',
                  'project': 'grace-gems', 'declaration_kind': 'agent-observed', 'completed_at': p['basis']['observed_at'],
                  'evidence': ref, 'invocation_ref': 'fixture-user-request', 'record_id': 'local-record', 'basis': p['basis'], 'native_session_ref': None}
    return config, completion, p, {'source-1': str(source)}


def prep(p, revision=1):
    return delivery.prepare(*p, 'test-host', AT, revision)


def capture(p, matches=None, outcome='not-attempted'):
    return {'account': p[0]['account'], 'folder_id': 'folder', 'drive_id': 'drive', 'observed_at': AT.isoformat(),
            'search_complete': True, 'name': 'hannah-current-contribution.json', 'matches': matches or [],
            'prior_write_outcome': outcome, 'downloaded_file_id': 'file-1'}


def metadata():
    return {'id': 'file-1', 'name': 'hannah-current-contribution.json', 'mime_type': 'application/json',
            'parent_ids': ['folder'], 'drive_id': 'drive', 'version': '1'}


def test_status_does_not_initialize(participant):
    assert delivery.status(participant[0], 'test-host', AT)['status'] == 'ready'
    assert not delivery.root_for(participant[0]).exists()


@pytest.mark.parametrize('failure', ['failed', 'missing', 'preadoption', 'memory', 'host', 'source', 'review'])
def test_delivery_completion_boundaries(participant, failure):
    c, close, p, sources = participant
    if failure == 'failed': close['status'] = 'failed'
    if failure == 'missing': close['evidence']['sha256'] = '0'*64
    if failure == 'preadoption': c['adopted_at'] = AT.isoformat()
    if failure == 'memory': close['trigger'] = 'memory-write'
    if failure == 'host': close['host'] = 'invented'
    if failure == 'source': p['sources'][0]['sha256'] = '0'*64; reviewed(p)
    if failure == 'review': p['outcomes'][0]['en'] = 'Changed'
    with pytest.raises(ValueError): prep(participant)
    assert not delivery.root_for(c).exists()


def test_upload_bootstrap_uncertainty_and_idempotence(participant):
    result = prep(participant); identifier = result['intent']; c = participant[0]
    assert prep(participant)['intent'] == identifier
    assert delivery.check_upload(c, identifier, capture(participant), None, AT)['action'] == 'create'
    with pytest.raises(ValueError): delivery.check_upload(c, identifier, capture(participant, outcome='uncertain'), None, AT)
    with pytest.raises(ValueError): delivery.check_upload(c, identifier, capture(participant, [metadata(), metadata()]), b'', AT)
    readback = capture(participant, [metadata()], 'uncertain')
    data = team.encoded(participant[2])
    assert delivery.record_upload(c, identifier, readback, data, AT)['action'] == 'verified'
    assert delivery.record_upload(c, identifier, readback, data, AT)['action'] == 'verified'
    again = prep(participant)['intent']
    assert delivery.check_upload(c, again, readback, data, AT)['action'] == 'verified'
    with pytest.raises(ValueError): delivery.check_upload(c, again, readback, b'independent edit', AT)


def test_revision_and_baseline(participant):
    first = prep(participant)['intent']; c = participant[0]; data = team.encoded(participant[2])
    delivery.record_upload(c, first, capture(participant, [metadata()]), data, AT)
    participant[2]['outcomes'][0]['en'] = 'Reviewed revision'; reviewed(participant[2])
    with pytest.raises(ValueError, match='higher revision'): prep(participant)
    next_id = prep(participant, 2)['intent']
    assert delivery.check_upload(c, next_id, capture(participant, [metadata()]), data, AT)['action'] == 'update'
    with pytest.raises(ValueError): delivery.check_upload(c, next_id, capture(participant, [{**metadata(), 'version': '2'}]), data, AT)


def test_fresh_repeated_receipt_and_source_location(participant, tmp_path):
    identifier = prep(participant)['intent']; c = participant[0]; data = team.encoded(participant[2])
    first = capture(participant, [metadata()])
    delivery.record_upload(c, identifier, first, data, AT)
    newer = {**first, 'observed_at': (AT + timedelta(minutes=1)).isoformat()}
    assert delivery.record_upload(c, identifier, newer, data, AT + timedelta(minutes=1))['action'] == 'verified'
    other = tmp_path / 'unadopted-source.txt'; other.write_bytes(Path(participant[3]['source-1']).read_bytes())
    participant[3]['source-1'] = str(other)
    with pytest.raises(ValueError, match='location'): prep(participant)


def test_shared_rollover():
    assert delivery.business_date(datetime(2026, 10, 29, 11, 59, tzinfo=timezone.utc)) == '2026-10-28'
    assert delivery.business_date(datetime(2026, 10, 29, 12, tzinfo=timezone.utc)) == '2026-10-29'
