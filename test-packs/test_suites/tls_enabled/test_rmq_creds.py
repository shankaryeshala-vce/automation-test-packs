from common_libs import cpsd


def test_rmq_creds():
    creds = cpsd.props.get_rmq_creds()
    print(creds)
