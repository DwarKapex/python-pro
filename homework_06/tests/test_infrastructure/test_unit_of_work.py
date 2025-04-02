import pytest
from infrastructure.unit_of_work import SqlAlchemyUnitOfWork
from pytest_mock import MockerFixture
from sqlalchemy.orm import Session


class TestSqlAlchemyUnitOfWork:
    def test_commit_calls_session_commit(self, mocker: MockerFixture):
        mock_session = mocker.Mock(spec=Session)
        uow = SqlAlchemyUnitOfWork(mock_session)
        uow.commit()
        mock_session.commit.assert_called_once()

    def test_rollback_calls_session_rollback(self, mocker: MockerFixture):
        mock_session = mocker.Mock(spec=Session)
        uow = SqlAlchemyUnitOfWork(mock_session)
        uow.rollback()
        mock_session.rollback.assert_called_once()

    def test_exit_commits_on_success(self, mocker: MockerFixture):
        mock_session = mocker.Mock(spec=Session)
        uow = SqlAlchemyUnitOfWork(mock_session)
        with uow:
            pass
        mock_session.commit.assert_called_once()
        mock_session.rollback.assert_not_called()
        mock_session.close.assert_called_once()

    def test_exit_rollbacks_on_exception(self, mocker: MockerFixture):
        mock_session = mocker.Mock(spec=Session)
        uow = SqlAlchemyUnitOfWork(mock_session)

        with pytest.raises(ValueError):
            with uow:
                raise ValueError("Test exception")

        mock_session.rollback.assert_called_once()
        mock_session.commit.assert_not_called()
        mock_session.close.assert_called_once()
