from __future__ import annotations

import os

from dotenv import load_dotenv
from openai import NotGiven, OpenAI
from pydantic import BaseModel

import prompts
from text_utils import extract_code

load_dotenv(override=True)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


class Step(BaseModel):
    title: str
    output: str


class CodeRevision(BaseModel):
    steps: list[Step]
    revised_code: str


class AnimationScore(BaseModel):
    similary_score: int


def _prompt_llm(
    prompt: str,
    system_message: str,
    temperature: float = 1.0,
    base64_images: list[str] = [],
    response_format=None,
) -> str:
    completion = client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        temperature=temperature,
        messages=[
            {"role": "system", "content": system_message},
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt,
                    },
                ]
                + [
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                    }
                    for base64_image in base64_images
                ],
            },  # type: ignore
        ],
        response_format=response_format or NotGiven(),  # type: ignore
    )
    if response_format:
        return completion.choices[0].message.parsed or ""

    return completion.choices[0].message.content or ""


# Design Phase Related


def generate_abstract_summary(
    description: str, duration: int, temperature: float, images: list[str]
) -> str:
    system_message = prompts.ABSTRACT_SUMMARY_SYSTEM_MESSAGE_TEMPLATE
    system_message = system_message.format(duration=float(duration))
    prompt = description
    return _prompt_llm(prompt, system_message, temperature, images)


def generate_centers_behavior(
    abstract_summary: str, temperature: float, images: list[str]
) -> str:
    system_message = prompts.CENTERS_BEHAVIOR_SYSTEM_MESSAGE
    prompt = abstract_summary
    return _prompt_llm(prompt, system_message, temperature, images)


def generate_rgbs_behavior(
    abstract_summary: str, temperature: float, images: list[str]
) -> str:
    system_message = prompts.RGBS_BEHAVIOR_SYSTEM_MESSAGE
    prompt = abstract_summary
    return _prompt_llm(prompt, system_message, temperature, images)


def generate_opacities_behavior(
    abstract_summary: str, temperature: float, images: list[str]
) -> str:
    system_message = prompts.OPACITIES_BEHAVIOR_SYSTEM_MESSAGE
    prompt = abstract_summary
    return _prompt_llm(prompt, system_message, temperature, images)


# Code Phase Related


def generate_centers_code(
    centers_behavior: str, duration: int, temperature: float, images: list[str]
) -> str:
    system_message = prompts.CENTERS_CODE_SYSTEM_MESSAGE
    system_message = system_message.format(duration=float(duration))
    prompt = centers_behavior
    centers_code_md = _prompt_llm(prompt, system_message, temperature, images)
    return extract_code(centers_code_md)


def generate_rgbs_code(
    rgbs_behavior: str, duration: int, temperature: float, images: list[str]
) -> str:
    system_message = prompts.RGBS_CODE_SYSTEM_MESSAGE
    system_message = system_message.format(duration=float(duration))
    prompt = rgbs_behavior
    rgbs_code_md = _prompt_llm(prompt, system_message, temperature, images)
    return extract_code(rgbs_code_md)


def generate_opacities_code(
    opacities_behavior: str, duration: int, temperature: float, images: list[str]
) -> str:
    system_message = prompts.OPACITIES_CODE_SYSTEM_MESSAGE
    system_message = system_message.format(duration=float(duration))
    prompt = opacities_behavior
    opacities_code_md = _prompt_llm(prompt, system_message, temperature, images)
    return extract_code(opacities_code_md)


# Auto Sample Related


def generate_animation_score(first_frames: list[str], description: str) -> int:
    system_message = prompts.SCORE_ANIMATION_SYSTEM_MESSAGE
    prompt = f'**Animation Description**: "{description}"'
    animation_score: AnimationScore = _prompt_llm(
        prompt,
        system_message,
        base64_images=first_frames,
        response_format=AnimationScore,
    )  # type: ignore
    return animation_score.similary_score


# Auto Improve Related


def generate_auto_improved_centers_code(
    centers_code: str, first_frames: list[str], description: str, temperature: float
) -> str:
    system_message = prompts.AUTO_IMPROVE_CENTERS_CODE_SYSTEM_MESSAGE
    prompt = prompts.AUTO_IMPROVE_USER_TEMPLATE
    prompt = prompt.format(description=description, function_code=centers_code)
    code_revision: CodeRevision = _prompt_llm(
        prompt,
        system_message,
        base64_images=first_frames,
        response_format=CodeRevision,
    )  # type: ignore
    return extract_code(code_revision.revised_code)


def generate_auto_improved_rgbs_code(
    rgbs_code: str, first_frames: list[str], description: str, temperature: float
) -> str:
    system_message = prompts.AUTO_IMPROVE_RGBS_CODE_SYSTEM_MESSAGE
    prompt = prompts.AUTO_IMPROVE_USER_TEMPLATE
    prompt = prompt.format(description=description, function_code=rgbs_code)
    code_revision: CodeRevision = _prompt_llm(
        prompt,
        system_message,
        base64_images=first_frames,
        response_format=CodeRevision,
    )  # type: ignore
    return extract_code(code_revision.revised_code)


def generate_auto_improved_opacities_code(
    opacities_code: str, first_frames: list[str], description: str, temperature: float
) -> str:
    system_message = prompts.AUTO_IMPROVE_OPACITIES_CODE_SYSTEM_MESSAGE
    prompt = prompts.AUTO_IMPROVE_USER_TEMPLATE
    prompt = prompt.format(description=description, function_code=opacities_code)
    code_revision: CodeRevision = _prompt_llm(
        prompt,
        system_message,
        base64_images=first_frames,
        response_format=CodeRevision,
    )  # type: ignore
    return extract_code(code_revision.revised_code)


# Feedback Loop Related


def generate_feedback_improved_centers_code(
    feedback: str,
    centers_code: str,
    first_frames: list[str],
    description: str,
    temperature: float,
) -> str:
    system_message = prompts.CENTERS_FEEDBACK_SYSTEM_MESSAGE
    prompt = prompts.FEEDBACK_USER_TEMPLATE
    prompt = prompt.format(
        description=description, function_code=centers_code, feedback=feedback
    )
    code_revision: CodeRevision = _prompt_llm(
        prompt,
        system_message,
        base64_images=first_frames,
        response_format=CodeRevision,
        temperature=temperature,
    )  # type: ignore
    return extract_code(code_revision.revised_code)


def generate_feedback_improved_rgbs_code(
    feedback: str,
    rgbs_code: str,
    first_frames: list[str],
    description: str,
    temperature: float,
) -> str:
    system_message = prompts.RGBS_FEEDBACK_SYSTEM_MESSAGE
    prompt = prompts.FEEDBACK_USER_TEMPLATE
    prompt = prompt.format(
        description=description, function_code=rgbs_code, feedback=feedback
    )
    code_revision: CodeRevision = _prompt_llm(
        prompt,
        system_message,
        base64_images=first_frames,
        response_format=CodeRevision,
        temperature=temperature,
    )  # type: ignore
    return extract_code(code_revision.revised_code)


def generate_feedback_improved_opacities_code(
    feedback: str,
    opacities_code: str,
    first_frames: list[str],
    description: str,
    temperature: float,
) -> str:
    system_message = prompts.OPACITIES_FEEDBACK_SYSTEM_MESSAGE
    prompt = prompts.FEEDBACK_USER_TEMPLATE
    prompt = prompt.format(
        description=description, function_code=opacities_code, feedback=feedback
    )
    code_revision: CodeRevision = _prompt_llm(
        prompt,
        system_message,
        base64_images=first_frames,
        response_format=CodeRevision,
        temperature=temperature,
    )  # type: ignore
    return extract_code(code_revision.revised_code)
