package com.aivle0102.bigproject.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Getter;
import lombok.Setter;

@Getter
@Setter
public class RecipeCaseRequest {
    private Long recipeId;
    private String recipe;
}