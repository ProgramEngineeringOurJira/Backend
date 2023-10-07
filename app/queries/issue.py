from uuid import UUID

from beanie import WriteRules

from app.core.exceptions import IssueNotFoundError, SprintNotFoundError, UserNotFoundError, ValidationError
from app.schemas.documents import Issue, Sprint, User, Workplace
from app.schemas.models.models import IssueCreation


async def create_new_issue(issue_creation: IssueCreation, workplace_id: UUID, user: User):
    workplace = await Workplace.find_one(Workplace.id == workplace_id, fetch_links=True)
    if issue_creation.state not in workplace.states:
        raise ValidationError("Указанного статуса нет существует.")
    users = [usr for usr in workplace.users if usr in issue_creation.users]
    if len(users) != len(issue_creation.users):
        raise UserNotFoundError("Указанный пользователь не не найден.")
    author = next(usr for usr in workplace.users if usr.user == user)
    issue = Issue(**issue_creation.model_dump(), author=author)
    await issue.create()
    workplace.issues.append(issue)
    await workplace.save()
    issue.implementers = users
    await issue.save(link_rule=WriteRules.WRITE)
    if issue_creation.sprint_id is not None:
        sprint = next((spr for spr in workplace.sprints if spr == issue_creation.sprint_id), None)
        if sprint is None:
            raise SprintNotFoundError("Такого спринта не найдено.")
        sprint.issues.append(issue)
        await sprint.save()


async def update_issue(issue_creation: IssueCreation, workplace_id: UUID, issue_id: UUID, user: User):
    issue = await Issue.find_one(Issue.id == issue_id, fetch_links=True)
    if issue is None:
        raise IssueNotFoundError("Такой задачи не найдено.")
    if issue.workplace.id != workplace_id:
        raise IssueNotFoundError("Задача принадлежит другому воркплейсу.")  # TODO forbidden
    if issue_creation.state not in issue.workplace.states:
        raise ValidationError("Указанного статуса нет существует.")
    users = [usr for usr in issue.workplace.users if usr in issue_creation.users]
    if len(users) != len(issue_creation.users):
        raise UserNotFoundError("Указанный пользовательне не найден.")
    if not isinstance(issue.sprint, Sprint) or issue_creation.sprint_id != issue.sprint.id:
        if isinstance(issue.sprint, Sprint):
            old_sprint = issue.sprint
            old_sprint.issues.remove(issue)
            await old_sprint.save()
        if issue_creation.sprint_id is not None:
            sprint = next((spr for spr in issue.workplace.sprints if spr == issue_creation.sprint_id), None)
            if sprint is None:
                raise SprintNotFoundError("Такого спринта не найдено.")
            sprint.issues.append(issue)
            await sprint.save()
    issue.implementers = users
    await issue.save(link_rule=WriteRules.WRITE)
    await issue.update({"$set": issue_creation.model_dump(exclude="sprint_id,users")})
