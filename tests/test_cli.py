from typer.testing import CliRunner
from nigeria_geodata.cli import app

runner = CliRunner()


# test launch
# test list data
# test search
# test filter success and failure
# test info succes and failure
def test_list_data():
    result = runner.invoke(app, ["list_data"])
    assert False
    print(result)
    # assert result.exit_code == 0
    # assert "Hello Camila" in result.stdout
    # assert "Let's have a coffee in Berlin" in result.stdout
