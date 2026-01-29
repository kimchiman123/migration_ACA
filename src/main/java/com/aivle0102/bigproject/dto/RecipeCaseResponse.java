package com.aivle0102.bigproject.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import com.aivle0102.bigproject.util.RecipeIngredientExtractor;

import lombok.Builder;
import lombok.Getter;

import java.util.List;

@Getter
@Builder
public class RecipeCaseResponse {
    private List<RegulatoryCase> productCases;

    private List<IngredientCases> ingredientCases;
}