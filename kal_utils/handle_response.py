from typing import TypeVar, Type, Callable, Tuple, Optional
from fastapi import status, Request
from pydantic import BaseModel, ValidationError

T = TypeVar('T', bound=BaseModel)

def parse_json_request(model: Type[T]) -> Callable[[Request], Tuple[Optional[T], list[str]]]:
    async def parser(request: Request) -> Tuple[Optional[T], list[str]]:
        try:
            json_data = await request.json()
            parsed_data = model(**json_data)
            return parsed_data, []
        except ValidationError as e:
            error_messages = []
            for error in e.errors():
                field = ".".join(str(loc) for loc in error["loc"])
                message = error["msg"]
                error_messages.append(f"{field}: {message}")
            return None, error_messages
        except Exception as e:
            return None, [f"An unexpected error occurred: {str(e)}"]

    return parser


def return_response(res=None, error=None, data=False):
    if error:
        return {"message": f"Internal Server Error: {error}", "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR}
    if res:
        response_status = res.get("status")
        del res["status"]
        if response_status == "success":
            res["status_code"] = status.HTTP_200_OK
            return res
        if data:
            res["status_code"] = status.HTTP_404_NOT_FOUND
            return res
        res["status_code"] = status.HTTP_400_BAD_REQUEST
        return res
